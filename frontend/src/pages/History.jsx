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
  Select 
} from 'antd';
import { 
  DownloadOutlined, 
  DeleteOutlined, 
  ReloadOutlined,
  HistoryOutlined,
  StopOutlined 
} from '@ant-design/icons';
import dayjs from 'dayjs';
import { getForecastHistory, downloadForecastResult, deleteForecastJob, cancelForecastJob } from '../services/api';

const { Option } = Select;

const History = () => {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState([]);
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 20,
    total: 0,
  });
  const [filterStatus, setFilterStatus] = useState(null);

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

  useEffect(() => {
    fetchHistory(1, 20, filterStatus);
  }, [filterStatus]);

  const handleTableChange = (newPagination) => {
    fetchHistory(newPagination.current, newPagination.pageSize, filterStatus);
  };

  const handleDownload = async (jobId) => {
    try {
      await downloadForecastResult(jobId);
      message.success('Download dimulai');
    } catch (error) {
      message.error('Download gagal');
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
          {/* Cancel button untuk PROCESSING jobs */}
          {record.status === 'PROCESSING' && (
            <Popconfirm
              title="Stop job ini?"
              description="Job akan dihentikan dan tidak bisa dilanjutkan"
              onConfirm={() => handleCancel(record.id)}
              okText="Ya, Stop"
              cancelText="Batal"
              okButtonProps={{ danger: true }}
            >
              <Button
                size="small"
                danger
                icon={<StopOutlined />}
              >
                Stop
              </Button>
            </Popconfirm>
          )}
          
          {/* Download button untuk COMPLETED jobs */}
          <Button
            size="small"
            icon={<DownloadOutlined />}
            disabled={record.status !== 'COMPLETED'}
            onClick={() => handleDownload(record.id)}
          >
            Download
          </Button>
          
          {/* Delete button */}
          {['COMPLETED', 'FAILED', 'CANCELLED'].includes(record.status) ? (
            <Popconfirm
              title="Hapus job ini?"
              description="File dan data akan dihapus permanen"
              onConfirm={() => handleDelete(record.id, false)}
              okText="Ya"
              cancelText="Tidak"
            >
              <Button
                size="small"
                danger
                icon={<DeleteOutlined />}
              >
                Hapus
              </Button>
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
              <Button
                size="small"
                danger
                icon={<DeleteOutlined />}
              >
                Force Delete
              </Button>
            </Popconfirm>
          )}
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
            <Button 
              icon={<ReloadOutlined />} 
              onClick={() => fetchHistory(pagination.current, pagination.pageSize, filterStatus)}
            >
              Refresh
            </Button>
          </Space>
        }
      >
        <Table
          columns={columns}
          dataSource={data}
          rowKey="id"
          loading={loading}
          pagination={pagination}
          onChange={handleTableChange}
          size="small"
        />
      </Card>
    </div>
  );
};

export default History;

