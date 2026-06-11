import request from './request'

export const login = (data) => {
  const formData = new FormData()
  formData.append('username', data.username)
  formData.append('password', data.password)
  return request({
    url: '/api/auth/login',
    method: 'post',
    data: formData,
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const register = (data) => {
  return request({
    url: '/api/auth/register',
    method: 'post',
    data,
  })
}

export const getProfile = () => {
  return request({
    url: '/api/auth/me',
    method: 'get',
  })
}

export const updateProfile = (data) => {
  return request({
    url: '/api/auth/me',
    method: 'put',
    data,
  })
}

export const getRoommates = () => {
  return request({
    url: '/api/auth/roommates',
    method: 'get',
  })
}
