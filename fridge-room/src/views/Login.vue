<template>
  <div class="auth-page">
    <div class="auth-header">
      <div class="logo">🧊</div>
      <h1>冰箱管家</h1>
      <p>合租室友的小冰箱大管家</p>
    </div>

    <van-form @submit="onSubmit" class="auth-form">
      <van-cell-group inset>
        <van-field
          v-model="form.username"
          name="username"
          label="账号"
          placeholder="请输入用户名"
          :rules="[{ required: true, message: '请填写用户名' }]"
        />
        <van-field
          v-model="form.password"
          type="password"
          name="password"
          label="密码"
          placeholder="请输入密码"
          :rules="[{ required: true, message: '请填写密码' }]"
        />
      </van-cell-group>

      <div class="auth-actions">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          登录
        </van-button>
        <div class="link-row">
          <router-link to="/register">没有账号？去注册</router-link>
        </div>
      </div>
    </van-form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const onSubmit = async () => {
  loading.value = true
  try {
    await userStore.doLogin(form)
    showToast('登录成功')
    const redirect = route.query.redirect || '/'
    router.replace(redirect)
  } catch (e) {
  } finally {
    loading.value = false
  }
}
</script>

<style lang="less" scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #e8f3ff 0%, #f7f8fa 40%);
  padding: 40px 0;
}

.auth-header {
  text-align: center;
  padding: 30px 0 20px;

  .logo {
    font-size: 72px;
    margin-bottom: 12px;
  }

  h1 {
    font-size: 28px;
    color: #1989fa;
    font-weight: 700;
  }

  p {
    color: #969799;
    font-size: 14px;
    margin-top: 8px;
  }
}

.auth-form {
  margin-top: 20px;
}

.auth-actions {
  padding: 24px 20px;

  .link-row {
    text-align: center;
    margin-top: 16px;

    a {
      color: #1989fa;
      font-size: 14px;
      text-decoration: none;
    }
  }
}
</style>
