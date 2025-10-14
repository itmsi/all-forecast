// frontend/src/services/api.js
/**
 * API Service untuk berkomunikasi dengan backend
 */

import axios from 'axios';

// Base URL untuk API
// Untuk development lokal, gunakan port 9571
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:9571';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Submit forecast job
 * @param {File} file - CSV file
 * @param {Object} config - Forecast configuration
 * @returns {Promise} Response dengan job_id dan task_id
 */
export const submitForecast = async (file, config) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('config', JSON.stringify(config));

  const response = await api.post('/api/forecast/submit', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Get forecast status by task_id
 * @param {string} taskId - Celery task ID
 * @returns {Promise} Status information
 */
export const getForecastStatus = async (taskId) => {
  const response = await api.get(`/api/forecast/status/${taskId}`);
  return response.data;
};

/**
 * Get forecast status by job_id
 * @param {number} jobId - Job ID
 * @returns {Promise} Status information
 */
export const getForecastStatusByJobId = async (jobId) => {
  const response = await api.get(`/api/forecast/status/job/${jobId}`);
  return response.data;
};

/**
 * Download forecast result
 * @param {number} jobId - Job ID
 */
export const downloadForecastResult = async (jobId) => {
  const response = await api.get(`/api/forecast/download/${jobId}`, {
    responseType: 'blob',
  });

  // Create download link
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `forecast_result_${jobId}.csv`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

/**
 * Get forecast history
 * @param {number} page - Page number
 * @param {number} pageSize - Page size
 * @param {string} status - Filter by status
 * @returns {Promise} History data
 */
export const getForecastHistory = async (page = 1, pageSize = 20, status = null) => {
  const params = { page, page_size: pageSize };
  if (status) params.status = status;

  const response = await api.get('/api/forecast/history', { params });
  return response.data;
};

/**
 * Cancel running forecast job
 * @param {number} jobId - Job ID
 * @returns {Promise}
 */
export const cancelForecastJob = async (jobId) => {
  const response = await api.post(`/api/forecast/cancel/${jobId}`);
  return response.data;
};

/**
 * Delete forecast job
 * @param {number} jobId - Job ID
 * @param {boolean} force - Force delete even if running
 * @returns {Promise}
 */
export const deleteForecastJob = async (jobId, force = false) => {
  const response = await api.delete(`/api/forecast/${jobId}`, {
    params: { force }
  });
  return response.data;
};

/**
 * Health check
 * @returns {Promise}
 */
export const healthCheck = async () => {
  const response = await api.get('/api/health');
  return response.data;
};

export default api;

