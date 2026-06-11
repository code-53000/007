import request from './request'

export const getFoods = (params = {}) => {
  return request({
    url: '/api/foods',
    method: 'get',
    params,
  })
}

export const getFoodDetail = (id) => {
  return request({
    url: `/api/foods/${id}`,
    method: 'get',
  })
}

export const createFood = (data) => {
  return request({
    url: '/api/foods',
    method: 'post',
    data,
  })
}

export const updateFood = (id, data) => {
  return request({
    url: `/api/foods/${id}`,
    method: 'put',
    data,
  })
}

export const cleanupFood = (id, data = {}) => {
  return request({
    url: `/api/foods/${id}/cleanup`,
    method: 'post',
    data,
  })
}

export const deleteFood = (id) => {
  return request({
    url: `/api/foods/${id}`,
    method: 'delete',
  })
}

export const getExpiryStats = () => {
  return request({
    url: '/api/foods/stats/expiry',
    method: 'get',
  })
}

export const getMyExpiring = (days = 3) => {
  return request({
    url: '/api/foods/mine/expiring',
    method: 'get',
    params: { days },
  })
}

export const getCategories = () => {
  return request({
    url: '/api/foods/categories',
    method: 'get',
  })
}
