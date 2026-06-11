<template>
  <div class="page-container">
    <van-nav-bar title="操作记录" left-arrow @click-left="$router.back()" fixed placeholder />

    <div class="card">
      <div class="section-title">
        <span>📊 近{{ days }}天概览</span>
        <van-dropdown-menu>
          <van-dropdown-item v-model="days" :options="dayOptions" />
        </van-dropdown-menu>
      </div>

      <div class="stat-total">
        <span class="num">{{ logsSummary.total_ops }}</span>
        <span class="label">次操作</span>
      </div>

      <div class="action-grid" v-if="actionList.length">
        <div
          v-for="a in actionList"
          :key="a.key"
          class="action-tile"
          @click="filterAction = filterAction === a.key ? '' : a.key"
          :class="{ active: filterAction === a.key }"
        >
          <div class="count">{{ a.count }}</div>
          <div class="name">{{ actionLabels[a.key] || a.key }}</div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="section-title">
        <span>📝 操作明细</span>
        <van-dropdown-menu>
          <van-dropdown-item v-model="filterType" :options="typeOptions" />
        </van-dropdown-menu>
      </div>

      <van-pull-refresh v-model="refreshing" @refresh="loadLogs">
        <van-list
          v-model:loading="loading"
          :finished="finished"
          finished-text="没有更多了"
          @load="loadLogs"
        >
          <div v-if="logs.length === 0" class="empty-state">
            <div class="empty-icon">📋</div>
            <div class="empty-text">暂无操作记录</div>
          </div>

          <div v-for="l in logs" :key="l.id" class="log-item">
            <div class="avatar" :style="{ background: l.user?.avatar_color }">
              {{ l.user?.nickname?.[0] || '?' }}
            </div>
            <div class="content">
              <div class="row1">
                <span class="user">{{ l.user?.nickname || '系统' }}</span>
                <span class="action" :class="actionClass(l.action)">
                  {{ actionLabels[l.action] || l.action }}
                </span>
                <span class="target">{{ targetLabels[l.target_type] || l.target_type }}</span>
              </div>
              <div class="detail" v-if="l.detail">💬 {{ l.detail }}</div>
              <div class="time">{{ formatTime(l.created_at) }}</div>
            </div>
          </div>
        </van-list>
      </van-pull-refresh>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import dayjs from 'dayjs'
import { getOperationLogs, getLogsSummary } from '@/api/shared'

const days = ref(7)
const dayOptions = [
  { text: '1天', value: 1 },
  { text: '7天', value: 7 },
  { text: '30天', value: 30 },
]

const filterAction = ref('')
const filterType = ref('all')
const typeOptions = [
  { text: '全部类型', value: 'all' },
  { text: '用户', value: 'user' },
  { text: '格子', value: 'box' },
  { text: '食物', value: 'food' },
  { text: '调料', value: 'seasoning' },
  { text: '空间', value: 'space_notice' },
]

const logs = ref([])
const logsSummary = ref({ total_ops: 0, by_action: {} })
const refreshing = ref(false)
const loading = ref(false)
const finished = ref(false)

const actionLabels = {
  register: '注册', login: '登录', update_profile: '修改资料',
  create_box: '建格子', update_box: '改格子', delete_box: '删格子',
  create_food: '放入食物', update_food: '改食物', cleanup_food: '清理食物', delete_food: '删食物',
  create_seasoning: '加调料', update_seasoning: '改调料', delete_seasoning: '删调料',
  create_space_notice: '发预告', update_space_notice: '改预告', delete_space_notice: '删预告',
}

const targetLabels = {
  user: '用户', box: '格子', food: '食物',
  seasoning: '调料', space_notice: '空间预告',
}

const actionList = computed(() => {
  const obj = logsSummary.value.by_action || {}
  return Object.entries(obj).map(([key, count]) => ({ key, count }))
    .sort((a, b) => b.count - a.count).slice(0, 8)
})

const actionClass = (a) => {
  if (a?.includes('delete')) return 'danger'
  if (a?.includes('create')) return 'primary'
  if (a?.includes('cleanup')) return 'warning'
  return 'normal'
}

const formatTime = (t) => dayjs(t).format('M月D日 HH:mm:ss')

const loadLogs = async () => {
  try {
    const params = { days: days.value, limit: 200 }
    if (filterType.value !== 'all') params.target_type = filterType.value
    if (filterAction.value) params.action = filterAction.value

    const [rec, sum] = await Promise.all([
      getOperationLogs(params),
      getLogsSummary(days.value),
    ])
    logs.value = rec
    logsSummary.value = sum
    finished.value = true
  } catch (e) {
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

onMounted(loadLogs)
</script>

<style lang="less" scoped>
.stat-total {
  text-align: center;
  padding: 16px;
  background: #f7f8fa;
  border-radius: 10px;
  margin-bottom: 12px;

  .num {
    font-size: 36px;
    font-weight: 700;
    color: #1989fa;
  }

  .label {
    color: #969799;
    font-size: 13px;
    margin-left: 6px;
  }
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.action-tile {
  background: #f7f8fa;
  padding: 10px 6px;
  border-radius: 8px;
  text-align: center;
  border: 2px solid transparent;
  transition: all 0.2s;

  &.active {
    background: #e8f3ff;
    border-color: #1989fa;
  }

  .count {
    font-size: 18px;
    font-weight: 700;
    color: #323233;
  }

  .name {
    font-size: 11px;
    color: #646566;
    margin-top: 2px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.log-item {
  display: flex;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f2f3f5;

  &:last-child { border-bottom: none; }

  .avatar {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    flex-shrink: 0;
  }

  .content {
    flex: 1;
    min-width: 0;

    .row1 {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;

      .user {
        font-size: 14px;
        font-weight: 600;
        color: #323233;
      }

      .action {
        padding: 1px 8px;
        border-radius: 10px;
        font-size: 11px;
        background: #ebedf0;
        color: #323233;

        &.primary { background: #e8f3ff; color: #1989fa; }
        &.warning { background: #fff3e8; color: #ff976a; }
        &.danger { background: #fde8e8; color: #ee0a24; }
      }

      .target {
        font-size: 11px;
        color: #969799;
        background: #f7f8fa;
        padding: 1px 6px;
        border-radius: 10px;
      }
    }

    .detail {
      font-size: 12px;
      color: #646566;
      margin-top: 3px;
    }

    .time {
      font-size: 12px;
      color: #c8c9cc;
      margin-top: 3px;
    }
  }
}
</style>
