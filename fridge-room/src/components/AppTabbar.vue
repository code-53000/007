<template>
  <van-tabbar v-model="active" route active-color="#1989fa" inactive-color="#646566">
    <van-tabbar-item to="/" icon="wap-home-o">冰箱</van-tabbar-item>
    <van-tabbar-item to="/expiry" icon="warning-o">
      过期
      <van-badge v-if="expiringCount > 0" :content="expiringCount" max="99" :offset="[-4, -4]" />
    </van-tabbar-item>
    <van-tabbar-item to="/shared" icon="friends-o">共享</van-tabbar-item>
    <van-tabbar-item to="/profile" icon="user-o">我的</van-tabbar-item>
  </van-tabbar>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getExpiryStats } from '@/api/foods'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const userStore = useUserStore()
const active = ref(0)
const stats = ref({})

const expiringCount = computed(() => {
  return (stats.value.warning || 0) + (stats.value.soon || 0) + (stats.value.expired || 0)
})

const loadStats = async () => {
  if (!userStore.isLoggedIn) return
  try {
    stats.value = await getExpiryStats()
  } catch (e) {}
}

onMounted(loadStats)
</script>
