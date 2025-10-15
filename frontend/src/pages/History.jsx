// frontend/src/pages/History.jsx
import React, { useState, useEffect } from 'react';
import { 
  Table, 
  Tag, 
  Button, 
  Space, 
  Card, 
  message,
  Popconfirm,
  Select,
  Tabs,
  Badge,
  Tooltip 
} from 'antd';
import { 
  DownloadOutlined, 
  DeleteOutlined, 
  ReloadOutlined,
  HistoryOutlined,
  StopOutlined,
  AppstoreOutlined,
  FileTextOutlined 
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { 
  getForecastHistory, 
  downloadForecastResult, 
  deleteForecastJob, 
  cancelForecastJob,
  getBatchHistory,
  downloadBatchResult,
  cancelBatchJob
} from '../services/api';

const { Option } = Select;

const History = () => {
  const [activeTab, setActiveTab] = useState('regular');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [batchData, setBatchData] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });
  const [batchPagination, setBatchPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });
  const [filterStatus, setFilterStatus] = useState(null);

  // Fetch regular forecast history
  const fetchHistory = async (page = 1, pageSize = 20, status = null) => {
    setLoading(true);
    try {
      const response = await getForecastHistory(page, pageSize, status);
      setData(response.jobs);
      setPagination({
        current: page,
        pageSize: pageSize,
        total: response.total,
      });
    } catch (error) {
      message.error('Gagal mengambil history');
    } finally {
      setLoading(false);
    }
  };

  // Fetch batch forecast history
  const fetchBatchHistory = async (page = 1, pageSize = 20) => {
    setLoading(true);
    try {
      const response = await getBatchHistory(page, pageSize);
      setBatchData(response.jobs);
      setBatchPagination({
        current: page,
        pageSize: pageSize,
        total: response.total,
      });
    } catch (error) {
      message.error('Gagal mengambil batch history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'regular') {
      fetchHistory(1, 20, filterStatus);
    } else {
      fetchBatchHistory(1, 20);
    }
  }, [filterStatus, activeTab]);

  const handleTableChange = (newPagination) => {
    fetchHistory(newPagination.current, newPagination.pageSize, filterStatus);
  };

  const handleBatchTableChange = (newPagination) => {
    fetchBatchHistory(newPagination.current, newPagination.pageSize);
  };

  const handleDownload = async (jobId) => {
    try {
      await downloadForecastResult(jobId);
      message.success('Download dimulai');
    } catch (error) {
      message.error('Download gagal');
    }
  };

  const handleBatchDownload = async (batchId) => {
    try {
      await downloadBatchResult(batchId);
      message.success('Download batch result dimulai');
    } catch (error) {
      message.error(`Download gagal: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleBatchCancel = async (batchId) => {
    try {
      await cancelBatchJob(batchId);
      message.success('Batch job berhasil dibatalkan');
      fetchBatchHistory(batchPagination.current, batchPagination.pageSize);
    } catch (error) {
      message.error(`Gagal membatalkan batch: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleCancel = async (jobId) => {
    try {
      await cancelForecastJob(jobId);
      message.success('Job berhasil dibatalkan');
      fetchHistory(pagination.current, pagination.pageSize, filterStatus);
    } catch (error) {
      message.error(`Gagal membatalkan job: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleDelete = async (jobId, force = false) => {
    try {
      await deleteForecastJob(jobId, force);
      message.success('Job berhasil dihapus');
      fetchHistory(pagination.current, pagination.pageSize, filterStatus);
    } catch (error) {
      message.error(`Gagal menghapus job: ${error.response?.data?.detail || error.message}`);
    }
  };

  // Regular forecast columns
  const columns = [
    {
      title: 'Job ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: 'File',
      dataIndex: 'filename',
      key: 'filename',
      ellipsis: true,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => {
        const colors = {
          'QUEUED': 'default',
          'PROCESSING': 'processing',
          'COMPLETED': 'success',
          'FAILED': 'error',
        };
        return <Tag color={colors[status]}>{status}</Tag>;
      },
    },
    {
      title: 'Dibuat',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date) => date ? dayjs(date).format('DD/MM/YYYY HH:mm') : '-',
    },
    {
      title: 'Selesai',
      dataIndex: 'completed_at',
      key: 'completed_at',
      width: 180,
      render: (date) => date ? dayjs(date).format('DD/MM/YYYY HH:mm') : '-',
    },
    {
      title: 'Horizon',
      key: 'horizon',
      width: 100,
      render: (_, record) => record.config?.forecast_horizon || '-',
    },
    {
      title: 'Aksi',
      key: 'action',
      width: 300,
      render: (_, record) => (
        <Space size="small">
          {record.status === 'PROCESSING' && (
            <Popconfirm
              title="Stop job ini?"
              description="Job akan dihentikan dan tidak bisa dilanjutkan"
              onConfirm={() => handleCancel(record.id)}
              okText="Ya, Stop"
              cancelText="Batal"
              okButtonProps={{ danger: true }}
            >
              <Button size="small" danger icon={<StopOutlined />}>Stop</Button>
            </Popconfirm>
          )}
          
          <Button
            size="small"
            icon={<DownloadOutlined />}
            disabled={record.status !== 'COMPLETED'}
            onClick={() => handleDownload(record.id)}
          >
            Download
          </Button>
          
          {['COMPLETED', 'FAILED', 'CANCELLED'].includes(record.status) ? (
            <Popconfirm
              title="Hapus job ini?"
              description="File dan data akan dihapus permanen"
              onConfirm={() => handleDelete(record.id, false)}
              okText="Ya"
              cancelText="Tidak"
            >
              <Button size="small" danger icon={<DeleteOutlined />}>Hapus</Button>
            </Popconfirm>
          ) : (
            <Popconfirm
              title="Force Delete?"
              description="Job masih running! Akan di-STOP dan HAPUS permanen. Yakin?"
              onConfirm={() => handleDelete(record.id, true)}
              okText="Ya, Force Delete"
              cancelText="Batal"
              okButtonProps={{ danger: true }}
            >
              <Button size="small" danger icon={<DeleteOutlined />}>Force Delete</Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  // Batch forecast columns
  const batchColumns = [
    {
      title: 'Batch ID',
      dataIndex: 'batch_job_id',
      key: 'batch_job_id',
      width: 80,
    },
    {
      title: 'File',
      dataIndex: 'original_filename',
      key: 'original_filename',
      ellipsis: true,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => {
        const colors = {
          'QUEUED': 'default',
          'PROCESSING': 'processing',
          'COMPLETED': 'success',
          'FAILED': 'error',
          'ROLLED_BACK': 'warning',
          'CANCELLED': 'default',
        };
        return <Tag color={colors[status]}>{status}</Tag>;
      },
    },
    {
      title: 'Partitions',
      key: 'partitions',
      width: 200,
      render: (_, record) => (
        <Space size={4}>
          <Tooltip title="Completed">
            <Badge count={record.completed_partitions || 0} showZero style={{ backgroundColor: '#52c41a' }} />
          </Tooltip>
          {record.skipped_partitions > 0 && (
            <Tooltip title="Skipped">
              <Badge count={record.skipped_partitions} showZero style={{ backgroundColor: '#faad14' }} />
            </Tooltip>
          )}
          {record.failed_partitions > 0 && (
            <Tooltip title="Failed">
              <Badge count={record.failed_partitions} showZero style={{ backgroundColor: '#f5222d' }} />
            </Tooltip>
          )}
          <span style={{ fontSize: '12px', color: '#999' }}>/ {record.total_partitions}</span>
        </Space>
      ),
    },
    {
      title: 'Dibuat',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date) => date ? dayjs(date).format('DD/MM/YYYY HH:mm') : '-',
    },
    {
      title: 'Selesai',
      dataIndex: 'completed_at',
      key: 'completed_at',
      width: 180,
      render: (date) => date ? dayjs(date).format('DD/MM/YYYY HH:mm') : '-',
    },
    {
      title: 'Aksi',
      key: 'action',
      width: 250,
      render: (_, record) => (
        <Space size="small">
          {record.status === 'PROCESSING' && (
            <Popconfirm
              title="Cancel batch ini?"
              description="Batch akan dihentikan"
              onConfirm={() => handleBatchCancel(record.batch_id)}
              okText="Ya, Cancel"
              cancelText="Batal"
              okButtonProps={{ danger: true }}
            >
              <Button size="small" danger icon={<StopOutlined />}>Cancel</Button>
            </Popconfirm>
          )}
          
          <Button
            type="primary"
            size="small"
            icon={<DownloadOutlined />}
            disabled={record.status !== 'COMPLETED'}
            onClick={() => handleBatchDownload(record.batch_id)}
          >
            Download
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px', maxWidth: 1400, margin: '0 auto' }}>
      <Card 
        title={
          <span>
            <HistoryOutlined /> Riwayat Forecast
          </span>
        }
        extra={
          <Space>
            {activeTab === 'regular' && (
              <Select
                style={{ width: 150 }}
                placeholder="Filter Status"
                allowClear
                onChange={setFilterStatus}
                value={filterStatus}
              >
                <Option value="QUEUED">Queued</Option>
                <Option value="PROCESSING">Processing</Option>
                <Option value="COMPLETED">Completed</Option>
                <Option value="FAILED">Failed</Option>
              </Select>
            )}
            <Button 
              icon={<ReloadOutlined />} 
              onClick={() => {
                if (activeTab === 'regular') {
                  fetchHistory(pagination.current, pagination.pageSize, filterStatus);
                } else {
                  fetchBatchHistory(batchPagination.current, batchPagination.pageSize);
                }
              }}
            >
              Refresh
            </Button>
          </Space>
        }
      >
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          items={[
            {
              key: 'regular',
              label: (
                <span>
                  <FileTextOutlined /> Regular Forecast
                </span>
              ),
              children: (
                <Table
                  columns={columns}
                  dataSource={data}
                  rowKey="id"
                  loading={loading}
                  pagination={pagination}
                  onChange={handleTableChange}
                  size="small"
                />
              ),
            },
            {
              key: 'batch',
              label: (
                <span>
                  <AppstoreOutlined /> Batch Forecast
                </span>
              ),
              children: (
                <Table
                  columns={batchColumns}
                  dataSource={batchData}
                  rowKey="batch_job_id"
                  loading={loading}
                  pagination={batchPagination}
                  onChange={handleBatchTableChange}
                  size="small"
                  expandable={{
                    expandedRowRender: (record) => (
                      <div style={{ padding: '8px 16px' }}>
                        <Space direction="vertical" style={{ width: '100%' }}>
                          <div>
                            <strong>Batch ID:</strong> {record.batch_id}
                          </div>
                          <div>
                            <strong>Strategy:</strong> {record.partition_strategy || 'site'}
                          </div>
                          <div>
                            <strong>Progress:</strong> {record.progress || 0}%
                          </div>
                          {record.error_message && (
                            <div style={{ color: '#f5222d' }}>
                              <strong>Error:</strong> {record.error_message}
                            </div>
                          )}
                        </Space>
                      </div>
                    ),
                    rowExpandable: (record) => true,
                  }}
                />
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
};

export default History;

