import request from './request'

export const getCleanupRecords = (params = {}) => {
  return request({
    url: '/api/cleanup/records',
    method: 'get',
    params,
  })
}

export const getCleanupStats = (days = 30) => {
  return request({
    url: '/api/cleanup/stats',
    method: 'get',
    params: { days },
  })
}

export const getCleanupRecord = (id) => {
  return request({
    url: `/api/cleanup/records/${id}`,
    method: 'get',
  })
}

export const getOperationLogs = (params = {}) => {
  return request({
    url: '/api/logs',
    method: 'get',
    params,
  })
}

export const getLogsSummary = (days = 7) => {
  return request({
    url: '/api/logs/summary',
    method: 'get',
    params: { days },
  })
}

export const getSeasonings = (params = {}) => {
  return request({
    url: '/api/seasonings',
    method: 'get',
    params,
  })
}

export const createSeasoning = (data) => {
  return request({
    url: '/api/seasonings',
    method: 'post',
    data,
  })
}

export const updateSeasoning = (id, data) => {
  return request({
    url: `/api/seasonings/${id}`,
    method: 'put',
    data,
  })
}

export const deleteSeasoning = (id) => {
  return request({
    url: `/api/seasonings/${id}`,
    method: 'delete',
  })
}

export const getSpaceNotices = (params = {}) => {
  return request({
    url: '/api/space-notices',
    method: 'get',
    params,
  })
}

export const createSpaceNotice = (data) => {
  return request({
    url: '/api/space-notices',
    method: 'post',
    data,
  })
}

export const updateSpaceNotice = (id, data) => {
  return request({
    url: `/api/space-notices/${id}`,
    method: 'put',
    data,
  })
}

export const deleteSpaceNotice = (id) => {
  return request({
    url: `/api/space-notices/${id}`,
    method: 'delete',
  })
}
