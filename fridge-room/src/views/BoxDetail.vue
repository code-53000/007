<template>
  <div class="page-container">
    <van-nav-bar
      :title="box?.name || '格子详情'"
      left-arrow
      @click-left="$router.back()"
      fixed
      placeholder
      :border="false"
    >
      <template #right>
        <van-icon name="edit" size="20" @click="showEdit = true" />
      </template>
    </van-nav-bar>

    <div v-if="box" class="box-detail">
      <div class="box-hero" :style="{ background: `linear-gradient(135deg, ${box.owner?.avatar_color || '#1989fa'}, #fff)` }">
        <div class="owner-avatar" :style="{ background: box.owner?.avatar_color || '#c8c9cc' }">
          {{ box.owner?.nickname?.[0] || '?' }}
        </div>
        <div class="box-info">
          <h2>{{ box.name }}</h2>
          <p>
            {{ box.owner?.nickname || '未分配' }} · 第{{ box.floor }}层 · 容量 {{ box.capacity }}
            <span v-if="box.is_public" class="badge">公共</span>
            <span v-else class="badge private">私有</span>
          </p>
          <p v-if="box.description" class="desc">{{ box.description }}</p>
        </div>
      </div>

      <div class="card">
        <div class="section-title">
          <span>格子里的食物 ({{ activeFoods.length }})</span>
          <van-button size="small" type="primary" @click="$router.push(`/food/add?box_id=${box.id}`)">
            + 放入
          </van-button>
        </div>

        <div v-if="activeFoods.length === 0" class="empty-state">
          <div class="empty-icon">🥗</div>
          <div class="empty-text">格子里还没有食物</div>
        </div>

        <div v-else class="food-list">
          <div
            v-for="f in activeFoods"
            :key="f.id"
            class="food-item"
            @click="showFoodMenu(f)"
          >
            <div class="food-icon">
              {{ categoryIcon(f.category) }}
            </div>
            <div class="food-main">
              <div class="food-name-row">
                <span class="name">{{ f.name }}</span>
                <span class="tag-status" :class="statusClass(f.expiry_status)">
                  {{ f.expiry_status }}
                </span>
              </div>
              <div class="food-meta">
                <span>{{ f.quantity }}{{ f.unit }}</span>
                <span>· {{ formatDate(f.stored_at) }}放入</span>
                <span>· {{ f.days_until_expiry < 0 ? `过期${-f.days_until_expiry}天` : `剩${f.days_until_expiry}天` }}</span>
              </div>
              <div class="food-owner" :style="{ color: f.owner?.avatar_color }">
                @{{ f.owner?.nickname }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <van-action-sheet
      v-model:show="actionSheet"
      :actions="actions"
      cancel-text="取消"
      @select="handleAction"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { showConfirmDialog, showToast, showDialog } from 'vant'
import { getBoxDetail } from '@/api/boxes'
import { cleanupFood, deleteFood } from '@/api/foods'
import dayjs from 'dayjs'

const route = useRoute()
const boxId = computed(() => route.params.id)
const box = ref(null)
const actionSheet = ref(false)
const currentFood = ref(null)

const activeFoods = computed(() => box.value?.foods || [])

const actions = computed(() => [
  { name: '标记已清理', action: 'cleanup' },
  { name: '查看详情', action: 'detail' },
  { name: '删除记录', action: 'delete', color: '#ee0a24' },
])

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

const formatDate = (d) => dayjs(d).format('M/D')

const loadData = async () => {
  try {
    box.value = await getBoxDetail(boxId.value)
  } catch (e) {}
}

const showFoodMenu = (f) => {
  currentFood.value = f
  actionSheet.value = true
}

const handleAction = async (a) => {
  if (!currentFood.value) return
  const f = currentFood.value

  if (a.action === 'cleanup') {
    try {
      await showConfirmDialog({
        title: '确认清理',
        message: `确定清理「${f.name}」吗？` + (f.days_until_expiry < 0 ? '（已过期）' : ''),
      })
      await cleanupFood(f.id)
      showToast('已清理')
      loadData()
    } catch (e) {}
  } else if (a.action === 'delete') {
    try {
      await showConfirmDialog({
        title: '删除确认',
        message: `确定删除「${f.name}」的记录吗？`,
      })
      await deleteFood(f.id)
      showToast('已删除')
      loadData()
    } catch (e) {}
  } else if (a.action === 'detail') {
    showDialog({
      title: f.name,
      message: `
数量：${f.quantity}${f.unit}
分类：${f.category}
放入：${dayjs(f.stored_at).format('YYYY年M月D日')}
保质天数：${f.expiry_days}天
过期时间：${dayjs(f.stored_at).add(f.expiry_days, 'day').format('YYYY年M月D日')}
状态：${f.expiry_status}
备注：${f.notes || '无'}
所有者：${f.owner?.nickname || '未知'}
      `.trim(),
    })
  }
}

watch(boxId, loadData)
onMounted(loadData)
</script>

<style lang="less" scoped>
.box-detail {
  .box-hero {
    padding: 20px 16px;
    display: flex;
    gap: 14px;
    align-items: center;

    .owner-avatar {
      width: 56px;
      height: 56px;
      border-radius: 16px;
      color: #fff;
      font-size: 28px;
      font-weight: 600;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    h2 {
      font-size: 20px;
      color: #323233;
      margin-bottom: 4px;
    }

    p {
      font-size: 13px;
      color: #646566;

      .badge {
        margin-left: 8px;
        padding: 1px 8px;
        background: #07c160;
        color: #fff;
        border-radius: 10px;
        font-size: 11px;

        &.private {
          background: #7232dd;
        }
      }

      &.desc {
        margin-top: 6px;
        color: #969799;
      }
    }
  }
}

.food-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.food-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #fafafa;
  border-radius: 12px;

  .food-icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    flex-shrink: 0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  }

  .food-main {
    flex: 1;
    min-width: 0;

    .food-name-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;

      .name {
        font-size: 15px;
        font-weight: 600;
        color: #323233;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    .food-meta {
      font-size: 12px;
      color: #969799;
      margin-top: 3px;
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
    }

    .food-owner {
      font-size: 12px;
      margin-top: 4px;
      font-weight: 500;
    }
  }
}
</style>
