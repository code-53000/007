<template>
  <div class="page-container">
    <van-nav-bar title="我的食物" left-arrow @click-left="$router.back()" fixed placeholder />

    <div class="card">
      <div class="section-title">
        <span>📊 我的食物统计</span>
      </div>

      <div class="stats-row">
        <div class="stat-item">
          <div class="num">{{ stats.total }}</div>
          <div class="label">总数</div>
        </div>
        <div class="stat-item">
          <div class="num" style="color:#969799">{{ stats.expired }}</div>
          <div class="label">已过期</div>
        </div>
        <div class="stat-item">
          <div class="num" style="color:#ee0a24">{{ stats.warning }}</div>
          <div class="label">临期</div>
        </div>
        <div class="stat-item">
          <div class="num" style="color:#ff976a">{{ stats.soon }}</div>
          <div class="label">即将到期</div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="section-title">
        <span>🍽️ 食物列表（按临期排序）</span>
      </div>

      <div v-if="foods.length === 0" class="empty-state">
        <div class="empty-icon">🧊</div>
        <div class="empty-text">冰箱里还没有你的食物，去添加一些吧~</div>
      </div>

      <div v-else class="food-list">
        <div
          v-for="f in foods"
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
              <span>{{ f.quantity }}{{ f.unit }}</span>
              <span>· {{ f.category }}</span>
            </div>
            <div class="meta2">
              <span>放入 {{ formatDate(f.stored_at) }}</span>
              <span>→ 到期 {{ formatDate(f.expiry_date) }}</span>
            </div>
            <div v-if="f.notes" class="notes">📝 {{ f.notes }}</div>
          </div>
          <div class="right-col">
            <van-button
              size="small"
              type="default"
              plain
              @click="onEdit(f)"
              style="margin-right: 6px"
            >
              编辑
            </van-button>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, showToast } from 'vant'
import dayjs from 'dayjs'
import { getMyFoods, cleanupFood } from '@/api/foods'

const router = useRouter()
const foods = ref([])

const stats = computed(() => {
  const s = { total: 0, expired: 0, warning: 0, soon: 0, normal: 0 }
  for (const f of foods.value) {
    s.total++
    if (f.expiry_status === '已过期') s.expired++
    else if (f.expiry_status === '临期') s.warning++
    else if (f.expiry_status === '即将到期') s.soon++
    else s.normal++
  }
  return s
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

const onEdit = (f) => {
  router.push(`/food/edit/${f.id}`)
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
    foods.value = await getMyFoods({ only_active: true })
  } catch (e) {}
}

onMounted(loadData)
</script>

<style lang="less" scoped>
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;

  .stat-item {
    text-align: center;
    padding: 12px 4px;
    background: #f7f8fa;
    border-radius: 10px;

    .num {
      font-size: 22px;
      font-weight: 700;
      color: #1989fa;
    }

    .label {
      font-size: 11px;
      color: #969799;
      margin-top: 4px;
    }
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

    .notes {
      font-size: 12px;
      color: #646566;
      margin-top: 4px;
    }
  }

  .right-col {
    flex-shrink: 0;
  }
}
</style>
