<template>
  <div class="page-container">
    <van-nav-bar title="清理记录" left-arrow @click-left="$router.back()" fixed placeholder />

    <div class="card">
      <div class="section-title">
        <span>📊 近{{ days }}天统计</span>
        <van-dropdown-menu>
          <van-dropdown-item v-model="days" :options="dayOptions" />
        </van-dropdown-menu>
      </div>

      <div class="stats-row">
        <div class="stat-item">
          <div class="num">{{ cleanupStats.total_cleanups }}</div>
          <div class="label">总清理次数</div>
        </div>
        <div class="stat-item">
          <div class="num" style="color:#ee0a24">{{ cleanupStats.expired_cleaned }}</div>
          <div class="label">清理过期物</div>
        </div>
      </div>

      <div class="rank-box" v-if="cleanupStats.by_operator?.length">
        <div class="rank-title">🏆 清理排行</div>
        <div
          v-for="(u, i) in cleanupStats.by_operator.slice(0, 5)"
          :key="u.user?.id"
          class="rank-item"
        >
          <div class="rank-no" :style="{ background: rankBg(i) }">{{ i + 1 }}</div>
          <div class="avatar" :style="{ background: u.user?.avatar_color }">
            {{ u.user?.nickname?.[0] }}
          </div>
          <span class="nickname">{{ u.user?.nickname }}</span>
          <span class="count">{{ u.count }} 次</span>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="section-title"><span>📝 清理明细</span></div>

      <van-pull-refresh v-model="refreshing" @refresh="loadRecords">
        <van-list
          v-model:loading="loading"
          :finished="finished"
          finished-text="没有更多了"
          @load="loadRecords"
        >
          <div v-if="records.length === 0" class="empty-state">
            <div class="empty-icon">🧹</div>
            <div class="empty-text">还没有清理记录</div>
          </div>

          <div v-for="r in records" :key="r.id" class="record-item">
            <div class="avatar" :style="{ background: r.operator?.avatar_color }">
              {{ r.operator?.nickname?.[0] }}
            </div>
            <div class="content">
              <div class="row1">
                <span class="user">{{ r.operator?.nickname }}</span>
                <span class="action">{{ r.action }}</span>
              </div>
              <div class="row2" v-if="r.note">💬 {{ r.note }}</div>
              <div class="time">{{ formatTime(r.created_at) }}</div>
            </div>
          </div>
        </van-list>
      </van-pull-refresh>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import dayjs from 'dayjs'
import { getCleanupRecords, getCleanupStats } from '@/api/shared'

const days = ref(30)
const dayOptions = [
  { text: '7天', value: 7 },
  { text: '15天', value: 15 },
  { text: '30天', value: 30 },
]
const records = ref([])
const cleanupStats = ref({ total_cleanups: 0, expired_cleaned: 0, by_operator: [] })
const refreshing = ref(false)
const loading = ref(false)
const finished = ref(false)

const rankBg = (i) => {
  const colors = ['#ffd700', '#c0c0c0', '#cd7f32', '#ebedf0', '#ebedf0']
  return colors[i] || '#ebedf0'
}

const formatTime = (t) => dayjs(t).format('M月D日 HH:mm')

const loadRecords = async () => {
  try {
    const [rec, stats] = await Promise.all([
      getCleanupRecords({ days: days.value, limit: 100 }),
      getCleanupStats(days.value),
    ])
    records.value = rec
    cleanupStats.value = stats
    finished.value = true
  } catch (e) {
  } finally {
    loading.value = false
    refreshing.value = false
  }
}

onMounted(loadRecords)
</script>

<style lang="less" scoped>
.stats-row {
  display: flex;
  gap: 12px;

  .stat-item {
    flex: 1;
    text-align: center;
    padding: 16px;
    background: #f7f8fa;
    border-radius: 10px;

    .num {
      font-size: 24px;
      font-weight: 700;
      color: #1989fa;
    }

    .label {
      font-size: 12px;
      color: #969799;
      margin-top: 4px;
    }
  }
}

.rank-box {
  margin-top: 16px;

  .rank-title {
    font-size: 14px;
    font-weight: 600;
    color: #323233;
    margin-bottom: 10px;
  }

  .rank-item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 8px 0;

    .rank-no {
      width: 22px;
      height: 22px;
      border-radius: 50%;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 600;
      flex-shrink: 0;
    }

    .avatar {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
    }

    .nickname {
      flex: 1;
      font-size: 14px;
      color: #323233;
    }

    .count {
      color: #969799;
      font-size: 13px;
    }
  }
}

.record-item {
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

    .row1 {
      display: flex;
      align-items: center;
      gap: 8px;

      .user {
        font-size: 14px;
        font-weight: 600;
        color: #323233;
      }

      .action {
        padding: 1px 8px;
        background: #e8f3ff;
        color: #1989fa;
        border-radius: 10px;
        font-size: 11px;
      }
    }

    .row2 {
      font-size: 13px;
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
