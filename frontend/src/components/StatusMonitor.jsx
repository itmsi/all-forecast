// frontend/src/components/StatusMonitor.jsx
import React from 'react';
import { Card, Progress, Tag, Descriptions, Alert } from 'antd';
import { 
  ClockCircleOutlined, 
  LoadingOutlined, 
  CheckCircleOutlined, 
  CloseCircleOutlined 
} from '@ant-design/icons';
import dayjs from 'dayjs';

const StatusMonitor = ({ status }) => {
  if (!status) return null;

  const getStatusTag = (statusText) => {
    const statusConfig = {
      'QUEUED': { color: 'default', icon: <ClockCircleOutlined /> },
      'PROCESSING': { color: 'processing', icon: <LoadingOutlined /> },
      'COMPLETED': { color: 'success', icon: <CheckCircleOutlined /> },
      'FAILED': { color: 'error', icon: <CloseCircleOutlined /> },
      'CANCELLED': { color: 'warning', icon: <CloseCircleOutlined /> }
    };

    const config = statusConfig[statusText] || statusConfig['QUEUED'];
    return <Tag color={config.color} icon={config.icon}>{statusText}</Tag>;
  };

  const formatDateTime = (dt) => {
    if (!dt) return '-';
    return dayjs(dt).format('DD/MM/YYYY HH:mm:ss');
  };

  const getDuration = () => {
    if (!status.started_at) return '-';
    const start = dayjs(status.started_at);
    const end = status.completed_at ? dayjs(status.completed_at) : dayjs();
    const duration = end.diff(start, 'second');
    
    if (duration < 60) return `${duration} detik`;
    if (duration < 3600) return `${Math.floor(duration / 60)} menit ${duration % 60} detik`;
    return `${Math.floor(duration / 3600)} jam ${Math.floor((duration % 3600) / 60)} menit`;
  };

  return (
    <Card title="Status Forecast" style={{ marginBottom: 16 }}>
      <Descriptions column={1} bordered size="small">
        <Descriptions.Item label="Job ID">{status.job_id}</Descriptions.Item>
        <Descriptions.Item label="Status">{getStatusTag(status.status)}</Descriptions.Item>
        <Descriptions.Item label="File">{status.filename}</Descriptions.Item>
        <Descriptions.Item label="Dibuat">{formatDateTime(status.created_at)}</Descriptions.Item>
        <Descriptions.Item label="Dimulai">{formatDateTime(status.started_at)}</Descriptions.Item>
        <Descriptions.Item label="Selesai">{formatDateTime(status.completed_at)}</Descriptions.Item>
        <Descriptions.Item label="Durasi">{getDuration()}</Descriptions.Item>
      </Descriptions>

      <div style={{ marginTop: 16 }}>
        <Progress 
          percent={status.progress || 0} 
          status={status.status === 'FAILED' ? 'exception' : 
                  status.status === 'COMPLETED' ? 'success' : 'active'}
          strokeColor={{
            '0%': '#108ee9',
            '100%': '#87d068',
          }}
        />
      </div>

      {status.error_message && (
        <Alert
          message="Error"
          description={status.error_message}
          type="error"
          showIcon
          style={{ marginTop: 16 }}
        />
      )}
    </Card>
  );
};

export default StatusMonitor;

