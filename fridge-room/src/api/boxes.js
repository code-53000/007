import request from './request'

export const getBoxes = (params = {}) => {
  return request({
    url: '/api/boxes',
    method: 'get',
    params,
  })
}

export const getBoxDetail = (id) => {
  return request({
    url: `/api/boxes/${id}`,
    method: 'get',
  })
}

export const createBox = (data) => {
  return request({
    url: '/api/boxes',
    method: 'post',
    data,
  })
}

export const updateBox = (id, data) => {
  return request({
    url: `/api/boxes/${id}`,
    method: 'put',
    data,
  })
}

export const deleteBox = (id) => {
  return request({
    url: `/api/boxes/${id}`,
    method: 'delete',
  })
}

export const getBoxStats = () => {
  return request({
    url: '/api/boxes/stats/summary',
    method: 'get',
  })
}
