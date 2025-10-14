// frontend/src/App.jsx
import React, { useState } from 'react';
import { Layout, Menu, Typography } from 'antd';
import { 
  DashboardOutlined, 
  HistoryOutlined 
} from '@ant-design/icons';
import Dashboard from './pages/Dashboard';
import History from './pages/History';
import './App.css';

const { Header, Content, Footer } = Layout;
const { Title } = Typography;

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: 'history',
      icon: <HistoryOutlined />,
      label: 'Riwayat',
    },
  ];

  const renderContent = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard />;
      case 'history':
        return <History />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ 
        display: 'flex', 
        alignItems: 'center',
        background: '#001529',
        padding: '0 50px'
      }}>
        <Title level={3} style={{ 
          color: 'white', 
          margin: '16px 24px 16px 0',
          minWidth: 200
        }}>
          Forecast System
        </Title>
        <Menu
          theme="dark"
          mode="horizontal"
          selectedKeys={[currentPage]}
          items={menuItems}
          onClick={({ key }) => setCurrentPage(key)}
          style={{ flex: 1, minWidth: 0 }}
        />
      </Header>
      
      <Content style={{ padding: '0 50px', background: '#f0f2f5' }}>
        {renderContent()}
      </Content>
      
      <Footer style={{ textAlign: 'center', background: '#001529', color: 'white' }}>
        Demand Forecasting System ©{new Date().getFullYear()} - Internal Use Only
      </Footer>
    </Layout>
  );
}

export default App;

