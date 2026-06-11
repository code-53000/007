<template>
  <div class="page-container">
    <div class="page-header" :style="{ background: `linear-gradient(135deg, ${bannerColor}, #fff)` }">
      <h1>⏰ 过期提醒</h1>
      <div class="subtitle">共 {{ stats.total }} 件食物 · {{ expiredCount }} 件需处理</div>
    </div>

    <div class="stats-row">
      <div
        v-for="s in statCards"
        :key="s.key"
        class="stat-card"
        :style="{ borderColor: s.color }"
        @click="filterBy(s.key)"
      >
        <div class="stat-val" :style="{ color: s.color }">{{ stats[s.key] || 0 }}</div>
        <div class="stat-label">{{ s.label }}</div>
      </div>
    </div>

    <div class="card">
      <div class="section-title">
        <span>{{ currentFilterLabel }}</span>
        <van-dropdown-menu>
          <van-dropdown-item v-model="filterCat" :options="catOptions" />
        </van-dropdown-menu>
      </div>

      <div v-if="filteredFoods.length === 0" class="empty-state">
        <div class="empty-icon">🎉</div>
        <div class="empty-text">太棒了，暂时没有需要处理的食物~</div>
      </div>

      <div v-else class="food-list">
        <div
          v-for="f in filteredFoods"
          :key="f.id"
          class="food-card"
          :class="statusClass(f.expiry_status)"
        >
          <div class="left-col">
            <div class="icon">{{ categoryIcon(f.category) }}</div>
            <div class="days-badge" :class="statusClass(f.expiry_status)">
              {{ f.days_until_expiry < 0 ? `${-f.days_until_expiry}天前` : `剩${f.days_until_expiry}天` }}
            </div>
          </div>
          <div class="mid-col">
            <div class="name">{{ f.name }}</div>
            <div class="meta">
              <span :style="{ color: f.owner?.avatar_color }">@{{ f.owner?.nickname }}</span>
              <span>· {{ f.quantity }}{{ f.unit }}</span>
            </div>
            <div class="meta2">
              <span>放入 {{ formatDate(f.stored_at) }}</span>
              <span>→ 到期 {{ formatDate(f.expiry_date) }}</span>
            </div>
          </div>
          <div class="right-col">
            <van-button
              size="small"
              :type="f.days_until_expiry < 0 ? 'danger' : 'primary'"
              plain
              @click="onCleanup(f)"
            >
              清理
            </van-button>
          </div>
        </div>
      </div>
    </div>

    <AppTabbar />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watchEffect } from 'vue'
import { showConfirmDialog, showToast } from 'vant'
import dayjs from 'dayjs'
import { getFoods, getExpiryStats, cleanupFood } from '@/api/foods'

const stats = ref({ total: 0, normal: 0, warning: 0, soon: 0, expired: 0 })
const foods = ref([])
const currentFilter = ref('expired')
const filterCat = ref(0)

const categories = [{ text: '全部分类', value: 0 }]
const catOptions = computed(() => categories)

const statusMap = {
  expired: '已过期', warning: '临期', soon: '即将到期', normal: '正常', all: '全部'
}

const bannerColor = computed(() => {
  if (stats.value.expired > 0) return '#ee0a24'
  if (stats.value.warning > 0) return '#ff976a'
  return '#1989fa'
})

const expiredCount = computed(() => stats.value.expired + stats.value.warning + stats.value.soon)

const currentFilterLabel = computed(() => statusMap[currentFilter.value])

const statCards = computed(() => [
  { key: 'expired', label: '已过期', color: '#969799' },
  { key: 'warning', label: '临期', color: '#ee0a24' },
  { key: 'soon', label: '即将到期', color: '#ff976a' },
  { key: 'normal', label: '正常', color: '#07c160' },
])

const filteredFoods = computed(() => {
  let list = foods.value
  if (currentFilter.value !== 'all') {
    list = list.filter(f => f.expiry_status === statusMap[currentFilter.value])
  }
  if (filterCat.value !== 0) {
    list = list.filter(f => f.category === filterCat.value)
  }
  return list
})

const statusClass = (s) => {
  const map = { '正常': 'normal', '即将到期': 'soon', '临期': 'warning', '已过期': 'expired' }
  return map[s] || 'normal'
}

const categoryIcon = (cat) => {
  const map = {
    '蔬菜': '🥬', '水果': '🍎', '肉类': '🥩', '蛋奶': '🥚',
    '主食': '🍚', '饮料': '🥤', '调料': '🧂', '剩菜': '🍱', '其他': '📦',
  }
  return map[cat] || '📦'
}

const formatDate = (d) => dayjs(d).format('M/D HH:mm')

const filterBy = (key) => {
  currentFilter.value = key
}

const onCleanup = async (f) => {
  try {
    await showConfirmDialog({
      title: '清理确认',
      message: `确定清理「${f.name}」吗？${f.days_until_expiry < 0 ? '（已过期）' : ''}`,
    })
    await cleanupFood(f.id)
    showToast('已清理')
    loadData()
  } catch (e) {}
}

const loadData = async () => {
  try {
    const [list, s] = await Promise.all([
      getFoods({ only_active: true }),
      getExpiryStats(),
    ])
    foods.value = list
    stats.value = s

    const catSet = new Set(list.map(f => f.category))
    categories.length = 1
    catSet.forEach(c => categories.push({ text: c, value: c }))
  } catch (e) {}
}

onMounted(loadData)
</script>

<style lang="less" scoped>
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  padding: 0 12px;
  margin-top: -10px;
}

.stat-card {
  background: #fff;
  border-radius: 10px;
  padding: 12px 8px;
  text-align: center;
  border-top: 3px solid #ddd;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);

  .stat-val {
    font-size: 22px;
    font-weight: 700;
    line-height: 1.1;
  }

  .stat-label {
    font-size: 11px;
    color: #969799;
    margin-top: 4px;
  }
}

.food-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.food-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  background: #fff;
  border-left: 4px solid #07c160;

  &.expired {
    border-left-color: #969799;
    background: #f7f8fa;
  }

  &.warning {
    border-left-color: #ee0a24;
  }

  &.soon {
    border-left-color: #ff976a;
  }

  .left-col {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    width: 52px;
    flex-shrink: 0;

    .icon {
      font-size: 30px;
    }

    .days-badge {
      padding: 2px 6px;
      border-radius: 10px;
      font-size: 11px;
      background: #e8f7ee;
      color: #07c160;
      font-weight: 600;

      &.expired {
        background: #f2f3f5;
        color: #969799;
      }

      &.warning {
        background: #fde8e8;
        color: #ee0a24;
      }

      &.soon {
        background: #fff3e8;
        color: #ff976a;
      }
    }
  }

  .mid-col {
    flex: 1;
    min-width: 0;

    .name {
      font-size: 15px;
      font-weight: 600;
      color: #323233;
    }

    .meta, .meta2 {
      font-size: 12px;
      color: #969799;
      margin-top: 3px;
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }
  }

  .right-col {
    flex-shrink: 0;
  }
}
</style>
