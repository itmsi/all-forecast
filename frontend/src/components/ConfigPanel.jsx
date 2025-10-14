// frontend/src/components/ConfigPanel.jsx
import React from 'react';
import { Form, InputNumber, Select, Input, Space, Tag } from 'antd';

const { Option } = Select;

const ConfigPanel = ({ config, onChange }) => {
  const handleChange = (field, value) => {
    onChange({ ...config, [field]: value });
  };

  const handleSiteCodesChange = (tags) => {
    onChange({ ...config, forecast_site_codes: tags });
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

        <Form.Item label="Zero Threshold" help="Prediksi di bawah nilai ini akan diset ke 0">
          <InputNumber
            min={0}
            max={10}
            step={0.1}
            value={config.zero_threshold}
            onChange={(value) => handleChange('zero_threshold', value)}
            style={{ width: '100%' }}
          />
        </Form.Item>

        <Form.Item label="Rounding Mode" help="Mode pembulatan hasil forecast">
          <Select
            value={config.rounding_mode}
            onChange={(value) => handleChange('rounding_mode', value)}
            style={{ width: '100%' }}
          >
            <Option value="half_up">Half Up (0.5 → 1)</Option>
            <Option value="round">Round (Standard)</Option>
            <Option value="ceil">Ceiling (Selalu naik)</Option>
            <Option value="floor">Floor (Selalu turun)</Option>
          </Select>
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

