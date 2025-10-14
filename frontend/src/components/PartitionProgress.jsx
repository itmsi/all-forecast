// frontend/src/components/PartitionProgress.jsx
import React from 'react';
import { Card, Progress, Tag, Table, Alert, Collapse, Descriptions } from 'antd';
import { 
  CheckCircleOutlined, 
  CloseCircleOutlined,
  LoadingOutlined,
  ClockCircleOutlined,
  WarningOutlined
} from '@ant-design/icons';

const { Panel } = Collapse;

const PartitionProgress = ({ batchStatus }) => {
  if (!batchStatus || !batchStatus.partition_results) return null;

  const getStatusIcon = (status) => {
    const icons = {
      'COMPLETED': <CheckCircleOutlined style={{ color: '#52c41a' }} />,
      'FAILED': <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
      'TIMEOUT': <WarningOutlined style={{ color: '#faad14' }} />,
      'PROCESSING': <LoadingOutlined style={{ color: '#1890ff' }} />,
      'PENDING': <ClockCircleOutlined style={{ color: '#d9d9d9' }} />
    };
    return icons[status] || icons['PENDING'];
  };

  const getStatusTag = (status) => {
    const colors = {
      'COMPLETED': 'success',
      'FAILED': 'error',
      'TIMEOUT': 'warning',
      'PROCESSING': 'processing',
      'PENDING': 'default'
    };
    return <Tag color={colors[status] || 'default'} icon={getStatusIcon(status)}>{status}</Tag>;
  };

  const columns = [
    {
      title: 'Partition',
      dataIndex: 'partition_id',
      key: 'partition_id',
      width: 100,
      render: (id) => `#${id}`
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 130,
      render: (status) => getStatusTag(status)
    },
    {
      title: 'Sites',
      key: 'sites',
      render: (_, record) => {
        const sites = record.metadata?.sites || [];
        if (sites.length === 0) return '-';
        if (sites.length === 1) return sites[0];
        return <span>{sites[0]} <Tag>{sites.length} sites</Tag></span>;
      }
    },
    {
      title: 'Rows',
      key: 'rows',
      width: 80,
      render: (_, record) => record.metadata?.rows?.toLocaleString() || '-'
    },
    {
      title: 'Parts',
      key: 'parts',
      width: 80,
      render: (_, record) => record.metadata?.partnumbers_count?.toLocaleString() || '-'
    },
    {
      title: 'Time',
      key: 'time',
      width: 100,
      render: (_, record) => {
        if (!record.execution_time) return '-';
        return `${record.execution_time}s`;
      }
    },
    {
      title: 'Error',
      key: 'error',
      render: (_, record) => {
        if (!record.error) return null;
        return (
          <Alert
            message={record.error}
            type="error"
            showIcon
            style={{ fontSize: 12 }}
          />
        );
      }
    }
  ];

  const failedPartitions = batchStatus.partition_results?.filter(p => 
    p.status === 'FAILED' || p.status === 'TIMEOUT'
  ) || [];

  const completedCount = batchStatus.completed_partitions || 0;
  const failedCount = batchStatus.failed_partitions || 0;
  const totalCount = batchStatus.total_partitions || 0;

  return (
    <Card 
      title={`Partition Progress (${completedCount}/${totalCount} completed)`}
      style={{ marginTop: 16, marginBottom: 16 }}
    >
      {/* Overall Progress */}
      <Descriptions bordered size="small" column={4} style={{ marginBottom: 16 }}>
        <Descriptions.Item label="Total Partitions">{totalCount}</Descriptions.Item>
        <Descriptions.Item label="Completed" contentStyle={{ color: '#52c41a' }}>
          {completedCount}
        </Descriptions.Item>
        <Descriptions.Item label="Failed" contentStyle={{ color: '#ff4d4f' }}>
          {failedCount}
        </Descriptions.Item>
        <Descriptions.Item label="Progress">
          {batchStatus.progress}%
        </Descriptions.Item>
      </Descriptions>

      {/* Failed Partitions Alert */}
      {failedPartitions.length > 0 && (
        <Alert
          message={`⚠️  ${failedPartitions.length} Partition(s) Failed/Timeout`}
          description={
            <div>
              <p>Partitions with issues:</p>
              <ul>
                {failedPartitions.map(p => (
                  <li key={p.partition_id}>
                    Partition #{p.partition_id}: {p.error || 'Timeout exceeded'}
                  </li>
                ))}
              </ul>
              {batchStatus.status === 'ROLLED_BACK' && (
                <p><strong>Status: Batch rolled back due to partition failures.</strong></p>
              )}
            </div>
          }
          type="error"
          showIcon
          style={{ marginBottom: 16 }}
        />
      )}

      {/* Partition Details Table */}
      <Collapse ghost defaultActiveKey={failedPartitions.length > 0 ? ['1'] : []}>
        <Panel header="Detail Partitions" key="1">
          <Table
            columns={columns}
            dataSource={batchStatus.partition_results}
            rowKey="partition_id"
            size="small"
            pagination={false}
            scroll={{ y: 400 }}
          />
        </Panel>
      </Collapse>
    </Card>
  );
};

export default PartitionProgress;

