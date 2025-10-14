// frontend/src/components/MetricsCard.jsx
import React from 'react';
import { Card, Statistic, Row, Col, Descriptions, Collapse } from 'antd';
import { 
  DashboardOutlined, 
  LineChartOutlined, 
  BarChartOutlined,
  TrophyOutlined 
} from '@ant-design/icons';

const { Panel } = Collapse;

const MetricsCard = ({ metrics }) => {
  if (!metrics || !metrics.best_model) return null;

  const bestModelMetrics = metrics.all_models?.[metrics.best_model];
  if (!bestModelMetrics) return null;

  const roundedMetrics = bestModelMetrics.rounded || {};

  return (
    <Card 
      title={
        <span>
          <TrophyOutlined style={{ marginRight: 8 }} />
          Metrics Model Terbaik: {metrics.best_model}
        </span>
      } 
      style={{ marginTop: 16, marginBottom: 16 }}
    >
      <Row gutter={16}>
        <Col span={6}>
          <Statistic
            title="MAE"
            value={roundedMetrics.MAE}
            precision={4}
            prefix={<DashboardOutlined />}
            valueStyle={{ color: '#3f8600' }}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="RMSE"
            value={roundedMetrics.RMSE}
            precision={4}
            prefix={<LineChartOutlined />}
            valueStyle={{ color: '#1890ff' }}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="MAPE%"
            value={roundedMetrics['MAPE%']}
            precision={2}
            suffix="%"
            prefix={<BarChartOutlined />}
            valueStyle={{ color: '#cf1322' }}
          />
        </Col>
        <Col span={6}>
          <Statistic
            title="sMAPE%"
            value={roundedMetrics['sMAPE%']}
            precision={2}
            suffix="%"
            prefix={<BarChartOutlined />}
            valueStyle={{ color: '#faad14' }}
          />
        </Col>
      </Row>

      {metrics.all_models && Object.keys(metrics.all_models).length > 1 && (
        <Collapse 
          style={{ marginTop: 16 }} 
          defaultActiveKey={[]}
          ghost
        >
          <Panel header="Lihat Semua Model" key="1">
            {Object.entries(metrics.all_models).map(([modelName, modelMetrics]) => (
              <div key={modelName} style={{ marginBottom: 16 }}>
                <h4>{modelName}</h4>
                <Descriptions size="small" column={4} bordered>
                  <Descriptions.Item label="MAE">
                    {modelMetrics.rounded?.MAE?.toFixed(4)}
                  </Descriptions.Item>
                  <Descriptions.Item label="RMSE">
                    {modelMetrics.rounded?.RMSE?.toFixed(4)}
                  </Descriptions.Item>
                  <Descriptions.Item label="MAPE%">
                    {modelMetrics.rounded?.['MAPE%']?.toFixed(2)}%
                  </Descriptions.Item>
                  <Descriptions.Item label="sMAPE%">
                    {modelMetrics.rounded?.['sMAPE%']?.toFixed(2)}%
                  </Descriptions.Item>
                </Descriptions>
              </div>
            ))}
          </Panel>
        </Collapse>
      )}
    </Card>
  );
};

export default MetricsCard;

