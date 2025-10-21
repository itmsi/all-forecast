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
  Popconfirm,
  Switch,
  Alert,
  Tooltip,
  Descriptions,
  Tag,
  Progress 
} from 'antd';
import { 
  RocketOutlined, 
  DownloadOutlined,
  InboxOutlined,
  StopOutlined 
} from '@ant-design/icons';
import ConfigPanel from '../components/ConfigPanel';
import StatusMonitor from '../components/StatusMonitor';
import MetricsCard from '../components/MetricsCard';
import PartitionProgress from '../components/PartitionProgress';
import { 
  submitForecast, 
  getForecastStatus, 
  downloadForecastResult, 
  cancelForecastJob,
  submitBatchForecast,
  getBatchStatus,
  downloadBatchResult,
  cancelBatchJob 
} from '../services/api';

const { Dragger } = Upload;
const { Title, Paragraph } = Typography;

const Dashboard = () => {
  const [file, setFile] = useState(null);
  const [config, setConfig] = useState({
    forecast_horizon: 7,
    forecast_site_codes: null,
    forecast_start_date: null,
    zero_threshold: 0.5,
    rounding_mode: 'half_up',
    random_state: 42,
    dayfirst: true
  });
  
  // Single forecast states
  const [taskId, setTaskId] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  
  // Batch forecast states
  const [batchMode, setBatchMode] = useState(false);
  const [batchId, setBatchId] = useState(null);
  const [batchStatus, setBatchStatus] = useState(null);
  const [batchAnalysis, setBatchAnalysis] = useState(null);
  
  // Common states
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
      // Prepare config
      const apiConfig = {
        ...config,
        forecast_site_codes: config.forecast_site_codes?.length > 0 
          ? config.forecast_site_codes 
          : null,
        forecast_start_date: config.forecast_start_date || null
      };

      if (batchMode) {
        // BATCH MODE: Auto-partition & parallel processing
        const response = await submitBatchForecast(
          file, 
          apiConfig,
          'site',  // partition by site
          2000,    // max 2000 rows per partition
          300      // 5 min timeout per partition
        );
        
        setBatchId(response.batch_id);
        setBatchAnalysis(response.analysis);
        setBatchStatus(null);
        
        message.success(
          `Batch forecast disubmit! ${response.analysis.total_partitions} partitions. ` +
          `Estimasi: ${response.analysis.estimated_time_minutes} menit`,
          5
        );
        
        // Start polling batch status
        startBatchPolling(response.batch_id);
        
      } else {
        // NORMAL MODE: Single forecast job
        const response = await submitForecast(file, apiConfig);
        
        setTaskId(response.task_id);
        setJobId(response.job_id);
        setStatus(null);
        
        message.success('Forecast job berhasil disubmit!');
        
        // Start polling status
        startPolling(response.task_id);
      }
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

  const startBatchPolling = (bid) => {
    setPolling(true);
    
    const interval = setInterval(async () => {
      try {
        const statusData = await getBatchStatus(bid);
        setBatchStatus(statusData);

        if (statusData.status === 'COMPLETED') {
          clearInterval(interval);
          setLoading(false);
          setPolling(false);
          message.success(
            `Batch forecast selesai! ${statusData.completed_partitions}/${statusData.total_partitions} partitions berhasil.`,
            5
          );
        } else if (statusData.status === 'FAILED' || statusData.status === 'ROLLED_BACK') {
          clearInterval(interval);
          setLoading(false);
          setPolling(false);
          message.error(
            `Batch forecast gagal. ${statusData.failed_partitions} partition(s) error. Lihat detail di bawah.`,
            7
          );
        } else if (statusData.status === 'CANCELLED') {
          clearInterval(interval);
          setLoading(false);
          setPolling(false);
          message.warning('Batch forecast dibatalkan');
        }
      } catch (error) {
        console.error('Error polling batch status:', error);
        clearInterval(interval);
        setLoading(false);
        setPolling(false);
        message.error('Gagal mengambil batch status');
      }
    }, 3000); // Poll every 3 seconds (batch takes longer)
  };

  const handleDownload = async () => {
    try {
      if (batchMode && batchId) {
        await downloadBatchResult(batchId);
        message.success('Download batch result dimulai');
      } else if (jobId) {
        await downloadForecastResult(jobId);
        message.success('Download dimulai');
      } else {
        message.error('Tidak ada hasil untuk didownload');
      }
    } catch (error) {
      message.error(`Download gagal: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleCancel = async () => {
    try {
      if (batchMode && batchId) {
        await cancelBatchJob(batchId);
        message.warning('Batch job dibatalkan');
        const statusData = await getBatchStatus(batchId);
        setBatchStatus(statusData);
        setLoading(false);
        setPolling(false);
      } else if (jobId) {
        await cancelForecastJob(jobId);
        message.warning('Job dibatalkan');
        const statusData = await getForecastStatus(taskId);
        setStatus(statusData);
        setLoading(false);
        setPolling(false);
      } else {
        message.error('Tidak ada job untuk dibatalkan');
      }
    } catch (error) {
      message.error(`Gagal membatalkan: ${error.response?.data?.detail || error.message}`);
    }
  };

  const handleReset = () => {
    setFile(null);
    setTaskId(null);
    setJobId(null);
    setStatus(null);
    setBatchId(null);
    setBatchStatus(null);
    setBatchAnalysis(null);
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
        
        <Divider />
        
        {/* Batch Mode Toggle */}
        <div style={{ marginTop: 16 }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div>
                <strong>Auto Batch Processing (Recommended untuk data besar)</strong>
                <br />
                <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                  Otomatis partisi data & process secara bertahap untuk avoid timeout
                </Typography.Text>
              </div>
              <Tooltip title="Enable untuk data >5000 rows atau >10 sites">
                <Switch 
                  checked={batchMode} 
                  onChange={setBatchMode}
                  checkedChildren="Batch ON"
                  unCheckedChildren="Batch OFF"
                />
              </Tooltip>
            </div>
            
            {batchMode && (
              <Alert
                message="Batch Mode Active"
                description={
                  <div>
                    <p>✅ Data akan di-partition otomatis per site (max 2000 rows/partition)</p>
                    <p>✅ Progress ditampilkan per partition</p>
                    <p>✅ Auto rollback jika ada partition yang fail</p>
                    <p>✅ Timeout protection: 5 menit per partition</p>
                    <p>⚠️  <strong>Note:</strong> Site Codes filter akan diabaikan (process all sites)</p>
                  </div>
                }
                type="info"
                showIcon
                style={{ marginTop: 8 }}
              />
            )}
            
            {batchAnalysis && (
              <Alert
                message="Batch Analysis"
                description={
                  <div>
                    <p>📊 Total rows: {batchAnalysis.total_rows?.toLocaleString()}</p>
                    <p>🏢 Sites: {batchAnalysis.unique_sites}</p>
                    <p>📦 Partnumbers: {batchAnalysis.unique_partnumbers?.toLocaleString()}</p>
                    <p>🔢 Partitions: {batchAnalysis.total_partitions}</p>
                    <p>⏱️  Estimated time: {batchAnalysis.estimated_time_minutes} min ({batchAnalysis.speedup_factor}x speedup)</p>
                  </div>
                }
                type="success"
                showIcon
                style={{ marginTop: 8 }}
              />
            )}
          </Space>
        </div>
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

          {(status?.status === 'PROCESSING' || batchStatus?.status === 'PROCESSING') && (
            <Popconfirm
              title={batchMode ? "Stop Batch Forecast?" : "Stop Forecast Job?"}
              description={
                batchMode 
                  ? "Semua partitions akan dihentikan dan tidak bisa dilanjutkan. Yakin?"
                  : "Job akan dihentikan dan tidak bisa dilanjutkan. Yakin?"
              }
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
                {batchMode ? 'Stop Batch' : 'Stop Job'}
              </Button>
            </Popconfirm>
          )}

          {(status?.status === 'COMPLETED' || batchStatus?.status === 'COMPLETED') && (
            <Button
              type="default"
              size="large"
              icon={<DownloadOutlined />}
              onClick={handleDownload}
            >
              Download Hasil
            </Button>
          )}

          {(status || taskId || batchStatus || batchId) && (
            <Button onClick={handleReset}>
              Reset
            </Button>
          )}
        </Space>
      </Card>

      {/* Single Forecast Status Monitor */}
      {!batchMode && status && <StatusMonitor status={status} />}

      {/* Batch Forecast Status */}
      {batchMode && batchStatus && (
        <Card title="Batch Forecast Status" style={{ marginBottom: 16 }}>
          <Descriptions bordered size="small" column={2}>
            <Descriptions.Item label="Batch ID">{batchStatus.batch_id?.substring(0, 8)}...</Descriptions.Item>
            <Descriptions.Item label="Status">
              <Tag color={
                batchStatus.status === 'COMPLETED' ? 'success' :
                batchStatus.status === 'FAILED' || batchStatus.status === 'ROLLED_BACK' ? 'error' :
                batchStatus.status === 'PROCESSING' ? 'processing' : 'default'
              }>
                {batchStatus.status}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Progress">{batchStatus.progress}%</Descriptions.Item>
            <Descriptions.Item label="Partitions">
              {batchStatus.completed_partitions}/{batchStatus.total_partitions} completed
            </Descriptions.Item>
          </Descriptions>
          
          <Progress 
            percent={batchStatus.progress} 
            status={
              batchStatus.status === 'FAILED' || batchStatus.status === 'ROLLED_BACK' ? 'exception' :
              batchStatus.status === 'COMPLETED' ? 'success' : 'active'
            }
            style={{ marginTop: 16 }}
          />
          
          {batchStatus.error_message && (
            <Alert
              message="Error"
              description={batchStatus.error_message}
              type="error"
              showIcon
              style={{ marginTop: 16 }}
            />
          )}
        </Card>
      )}

      {/* Partition Progress Detail */}
      {batchMode && batchStatus && <PartitionProgress batchStatus={batchStatus} />}

      {/* Metrics */}
      {status?.metrics && <MetricsCard metrics={status.metrics} />}
    </div>
  );
};

export default Dashboard;

