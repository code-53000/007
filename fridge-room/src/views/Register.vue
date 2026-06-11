<template>
  <div class="auth-page">
    <van-nav-bar
      title="注册账号"
      left-arrow
      @click-left="$router.back()"
      fixed
      placeholder
    />

    <div class="auth-header">
      <div class="logo">📝</div>
      <h2>加入冰箱管家</h2>
      <p>和室友一起管理好冰箱</p>
    </div>

    <van-form @submit="onSubmit" class="auth-form">
      <van-cell-group inset>
        <van-field
          v-model="form.username"
          label="用户名"
          placeholder="用于登录，2-50字"
          :rules="[{ required: true, message: '请填写用户名' }, { min: 2, max: 50, message: '长度2-50字' }]"
        />
        <van-field
          v-model="form.nickname"
          label="昵称"
          placeholder="显示在冰箱里的名字"
          :rules="[{ required: true, message: '请填写昵称' }]"
        />
        <van-field
          v-model="form.password"
          type="password"
          label="密码"
          placeholder="至少4位"
          :rules="[{ required: true, message: '请填写密码' }, { min: 4, message: '密码至少4位' }]"
        />
        <van-field
          v-model="form.room_number"
          label="房间号"
          placeholder="例如：A301（可选）"
        />
      </van-cell-group>

      <div class="color-picker">
        <div class="label">选择头像颜色</div>
        <div class="colors">
          <div
            v-for="c in colors"
            :key="c"
            class="color-item"
            :class="{ active: form.avatar_color === c }"
            :style="{ background: c }"
            @click="form.avatar_color = c"
          />
        </div>
      </div>

      <div class="auth-actions">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          注册并登录
        </van-button>
        <div class="link-row">
          <router-link to="/login">已有账号？去登录</router-link>
        </div>
      </div>
    </van-form>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)

const colors = ['#1989fa', '#07c160', '#ff976a', '#ee0a24', '#7232dd', '#606266']

const form = reactive({
  username: '',
  nickname: '',
  password: '',
  room_number: '',
  avatar_color: colors[0],
})

const onSubmit = async () => {
  loading.value = true
  try {
    await userStore.doRegister(form)
    showToast('注册成功')
    router.replace('/')
  } catch (e) {
  } finally {
    loading.value = false
  }
}
</script>

<style lang="less" scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #e8fff0 0%, #f7f8fa 40%);
}

.auth-header {
  text-align: center;
  padding: 20px 0 10px;

  .logo {
    font-size: 56px;
    margin-bottom: 8px;
  }

  h2 {
    font-size: 22px;
    color: #07c160;
    font-weight: 600;
  }

  p {
    color: #969799;
    font-size: 13px;
    margin-top: 4px;
  }
}

.auth-form {
  margin-top: 16px;
}

.color-picker {
  padding: 12px 20px;

  .label {
    font-size: 13px;
    color: #969799;
    margin-bottom: 10px;
  }

  .colors {
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }

  .color-item {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 3px solid transparent;
    transition: all 0.2s;
    cursor: pointer;

    &.active {
      border-color: #fff;
      box-shadow: 0 0 0 2px #323233;
      transform: scale(1.1);
    }
  }
}

.auth-actions {
  padding: 16px 20px 30px;

  .link-row {
    text-align: center;
    margin-top: 14px;

    a {
      color: #1989fa;
      font-size: 14px;
      text-decoration: none;
    }
  }
}
</style>
