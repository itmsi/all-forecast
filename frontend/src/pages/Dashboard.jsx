// frontend/src/pages/Dashboard.jsx
import React, { useState } from 'react';
import { 
  Card, 
  Upload, 
  Button, 
  message, 
  Space, 
  Divider,
  Typography,
  Popconfirm 
} from 'antd';
import { 
  UploadOutlined, 
  RocketOutlined, 
  DownloadOutlined,
  InboxOutlined,
  StopOutlined 
} from '@ant-design/icons';
import ConfigPanel from '../components/ConfigPanel';
import StatusMonitor from '../components/StatusMonitor';
import MetricsCard from '../components/MetricsCard';
import { submitForecast, getForecastStatus, downloadForecastResult, cancelForecastJob } from '../services/api';

const { Dragger } = Upload;
const { Title, Paragraph } = Typography;

const Dashboard = () => {
  const [file, setFile] = useState(null);
  const [config, setConfig] = useState({
    forecast_horizon: 7,
    forecast_site_codes: null,
    zero_threshold: 0.5,
    rounding_mode: 'half_up',
    random_state: 42,
    dayfirst: true
  });
  const [taskId, setTaskId] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [polling, setPolling] = useState(false);

  const uploadProps = {
    name: 'file',
    multiple: false,
    accept: '.csv',
    beforeUpload: (file) => {
      // Validate file type
      if (!file.name.endsWith('.csv')) {
        message.error('Hanya file CSV yang diizinkan!');
        return false;
      }

      // Validate file size (max 50MB)
      const isLt50M = file.size / 1024 / 1024 < 50;
      if (!isLt50M) {
        message.error('File harus lebih kecil dari 50MB!');
        return false;
      }

      setFile(file);
      message.success(`${file.name} berhasil dipilih`);
      return false; // Prevent auto upload
    },
    onRemove: () => {
      setFile(null);
    },
    fileList: file ? [file] : [],
  };

  const handleSubmit = async () => {
    if (!file) {
      message.error('Silakan upload file CSV terlebih dahulu');
      return;
    }

    setLoading(true);
    try {
      // Prepare config (convert null site_codes to empty array for API)
      const apiConfig = {
        ...config,
        forecast_site_codes: config.forecast_site_codes?.length > 0 
          ? config.forecast_site_codes 
          : null
      };

      const response = await submitForecast(file, apiConfig);
      
      setTaskId(response.task_id);
      setJobId(response.job_id);
      setStatus(null);
      
      message.success('Forecast job berhasil disubmit!');
      
      // Start polling status
      startPolling(response.task_id);
    } catch (error) {
      message.error(`Gagal submit forecast: ${error.response?.data?.detail || error.message}`);
      setLoading(false);
    }
  };

  const startPolling = (tid) => {
    setPolling(true);
    
    const interval = setInterval(async () => {
      try {
        const statusData = await getForecastStatus(tid);
        setStatus(statusData);

        if (statusData.status === 'COMPLETED') {
          clearInterval(interval);
          setLoading(false);
          setPolling(false);
          message.success('Forecast selesai! Silakan download hasil.', 5);
        } else if (statusData.status === 'FAILED') {
          clearInterval(interval);
          setLoading(false);
          setPolling(false);
          message.error('Forecast gagal. Lihat detail error di bawah.', 5);
        }
      } catch (error) {
        console.error('Error polling status:', error);
        clearInterval(interval);
        setLoading(false);
        setPolling(false);
        message.error('Gagal mengambil status');
      }
    }, 2000); // Poll every 2 seconds
  };

  const handleDownload = async () => {
    if (!jobId) {
      message.error('Tidak ada hasil untuk didownload');
      return;
    }

    try {
      await downloadForecastResult(jobId);
      message.success('Download dimulai');
    } catch (error) {
      message.error(`Download gagal: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleCancel = async () => {
    if (!jobId) {
      message.error('Tidak ada job untuk dibatalkan');
      return;
    }

    try {
      await cancelForecastJob(jobId);
      message.warning('Job dibatalkan');
      
      // Refresh status
      const statusData = await getForecastStatus(taskId);
      setStatus(statusData);
      setLoading(false);
      setPolling(false);
    } catch (error) {
      message.error(`Gagal membatalkan job: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleReset = () => {
    setFile(null);
    setTaskId(null);
    setJobId(null);
    setStatus(null);
    setLoading(false);
    setPolling(false);
  };

  return (
    <div style={{ padding: '24px', maxWidth: 1200, margin: '0 auto' }}>
      <Title level={2}>
        <RocketOutlined /> Demand Forecasting System
      </Title>
      <Paragraph type="secondary">
        Upload data demand historis dalam format CSV, konfigurasi parameter forecast, 
        dan dapatkan prediksi demand untuk periode mendatang.
      </Paragraph>

      <Divider />

      {/* Upload Section */}
      <Card title="1. Upload Data" style={{ marginBottom: 16 }}>
        <Dragger {...uploadProps} style={{ marginBottom: 16 }}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p className="ant-upload-text">Klik atau drag file CSV ke area ini</p>
          <p className="ant-upload-hint">
            File harus berisi kolom: date, partnumber, site_code, demand_qty
          </p>
        </Dragger>
      </Card>

      {/* Config Section */}
      <Card title="2. Konfigurasi Forecast" style={{ marginBottom: 16 }}>
        <ConfigPanel config={config} onChange={setConfig} />
      </Card>

      {/* Action Buttons */}
      <Card style={{ marginBottom: 16 }}>
        <Space size="large">
          <Button
            type="primary"
            size="large"
            icon={<RocketOutlined />}
            onClick={handleSubmit}
            loading={loading}
            disabled={!file || polling}
          >
            {loading ? 'Processing...' : 'Jalankan Forecast'}
          </Button>

          {status?.status === 'PROCESSING' && (
            <Popconfirm
              title="Stop Forecast Job?"
              description="Job akan dihentikan dan tidak bisa dilanjutkan. Yakin?"
              onConfirm={handleCancel}
              okText="Ya, Stop"
              cancelText="Batal"
              okButtonProps={{ danger: true }}
            >
              <Button
                danger
                size="large"
                icon={<StopOutlined />}
                loading={false}
              >
                Stop Job
              </Button>
            </Popconfirm>
          )}

          {status?.status === 'COMPLETED' && (
            <Button
              type="default"
              size="large"
              icon={<DownloadOutlined />}
              onClick={handleDownload}
            >
              Download Hasil
            </Button>
          )}

          {(status || taskId) && (
            <Button onClick={handleReset}>
              Reset
            </Button>
          )}
        </Space>
      </Card>

      {/* Status Monitor */}
      {status && <StatusMonitor status={status} />}

      {/* Metrics */}
      {status?.metrics && <MetricsCard metrics={status.metrics} />}
    </div>
  );
};

export default Dashboard;

