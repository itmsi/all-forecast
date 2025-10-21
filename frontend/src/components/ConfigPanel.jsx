// frontend/src/components/ConfigPanel.jsx
import React from 'react';
import { Form, InputNumber, Select, DatePicker } from 'antd';
import dayjs from 'dayjs';

const { Option } = Select;

const ConfigPanel = ({ config, onChange }) => {
  const handleChange = (field, value) => {
    onChange({ ...config, [field]: value });
  };

  const handleSiteCodesChange = (tags) => {
    onChange({ ...config, forecast_site_codes: tags });
  };

  const handleDateChange = (date, dateString) => {
    // Only set the date if it's not empty
    onChange({ ...config, forecast_start_date: dateString || null });
  };

  return (
    <div style={{ marginTop: 16 }}>
      <h3>Konfigurasi Forecast</h3>
      
      <Form layout="vertical">
        <Form.Item label="Forecast Horizon (hari)" help="Jumlah hari ke depan yang akan di-forecast">
          <InputNumber
            min={1}
            max={90}
            value={config.forecast_horizon}
            onChange={(value) => handleChange('forecast_horizon', value)}
            style={{ width: '100%' }}
          />
        </Form.Item>

        <Form.Item 
          label="Forecast Start Date" 
          help="Tanggal mulai forecast (format: DD/MM/YYYY). Kosongkan untuk menggunakan tanggal otomatis"
        >
          <DatePicker
            format="DD/MM/YYYY"
            placeholder="Pilih tanggal mulai forecast"
            value={config.forecast_start_date ? dayjs(config.forecast_start_date, 'DD/MM/YYYY') : null}
            onChange={handleDateChange}
            style={{ width: '100%' }}
            allowClear
          />
        </Form.Item>

        <Form.Item 
          label="Site Codes" 
          help="Kosongkan untuk semua site, atau masukkan kode site terpisah koma (contoh: IEL-ST-KDI,IEL-MU-SFI)"
        >
          <Select
            mode="tags"
            style={{ width: '100%' }}
            placeholder="Masukkan kode site atau kosongkan untuk semua"
            value={config.forecast_site_codes || []}
            onChange={handleSiteCodesChange}
            tokenSeparators={[',']}
          />
        </Form.Item>

        <Form.Item label="Format Tanggal" help="Format parsing tanggal di CSV">
          <Select
            value={config.dayfirst}
            onChange={(value) => handleChange('dayfirst', value)}
            style={{ width: '100%' }}
          >
            <Option value={true}>Day First (DD/MM/YYYY)</Option>
            <Option value={false}>Month First (MM/DD/YYYY)</Option>
          </Select>
        </Form.Item>
      </Form>
    </div>
  );
};

export default ConfigPanel;

