<template>
  <div class="page-container">
    <div class="page-header" style="background: linear-gradient(135deg, #7232dd, #c39bd3);">
      <div class="header-top">
        <div class="header-title">
          <h1>🤝 共享空间</h1>
          <div class="subtitle">公共调料 & 即将腾出的空间</div>
        </div>
        <div class="user-avatar" :style="{ background: userStore.avatarColor }" @click="$router.push('/profile')">
          {{ userStore.user?.nickname?.[0] || '?' }}
        </div>
      </div>
    </div>

    <van-tabs v-model:active="activeTab">
      <van-tab title="公共调料" name="seasoning">
        <div class="card">
          <div class="section-title">
            <span>🧂 调料列表 ({{ seasonings.length }})</span>
            <van-button size="small" type="primary" plain @click="openSeasoningForm()">
              + 添加
            </van-button>
          </div>

          <div v-if="seasonings.length === 0" class="empty-state">
            <div class="empty-icon">🧂</div>
            <div class="empty-text">还没有登记公共调料</div>
          </div>

          <div v-else class="list">
            <div
              v-for="s in seasonings"
              :key="s.id"
              class="list-item seasoning"
              :class="{ depleted: s.is_depleted }"
              @click="openSeasoningForm(s)"
            >
              <div class="avatar">🧂</div>
              <div class="content">
                <div class="row1">
                  <span class="name">{{ s.name }}</span>
                  <span v-if="s.is_depleted" class="tag-exp">已用完</span>
                  <span v-else-if="isNearExpiry(s.expiry_date)" class="tag-warn">快过期</span>
                </div>
                <div class="row2">
                  <span>{{ s.category }}</span>
                  <span v-if="s.brand">· {{ s.brand }}</span>
                  <span v-if="s.quantity">· {{ s.quantity }}</span>
                </div>
                <div class="row3">
                  <span :style="{ color: s.adder?.avatar_color }">@{{ s.adder?.nickname }}</span>
                  <span v-if="s.location_note">· 📍{{ s.location_note }}</span>
                  <span v-if="s.expiry_date">· 📅{{ formatDate(s.expiry_date) }}</span>
                </div>
              </div>
              <div class="item-actions" @click.stop>
                <van-button
                  size="mini"
                  :type="s.is_depleted ? 'success' : 'warning'"
                  plain
                  @click="toggleSeasoningDepleted(s, $event)"
                >
                  {{ s.is_depleted ? '恢复' : '用完' }}
                </van-button>
                <van-button
                  size="mini"
                  type="danger"
                  plain
                  @click="deleteSeasoningItem(s, $event)"
                >
                  删除
                </van-button>
              </div>
            </div>
          </div>
        </div>
      </van-tab>

      <van-tab title="空间预告" name="space">
        <div class="card">
          <div class="section-title">
            <span>📬 即将腾出 ({{ spaces.length }})</span>
            <van-button size="small" type="primary" plain @click="openSpaceForm()">
              + 发布
            </van-button>
          </div>

          <div v-if="spaces.length === 0" class="empty-state">
            <div class="empty-icon">📬</div>
            <div class="empty-text">暂时没有人要腾空间</div>
          </div>

          <div v-else class="list">
            <div
              v-for="n in spaces"
              :key="n.id"
              class="list-item space"
              :class="{ freed: n.is_freed }"
              @click="openSpaceForm(n)"
            >
              <div class="avatar">📦</div>
              <div class="content">
                <div class="row1">
                  <span class="name">{{ n.space_size || '一个格子位' }}</span>
                  <span v-if="n.is_freed" class="tag-exp">已释放</span>
                  <span v-else-if="isPastDate(n.free_up_date)" class="tag-warn">今日可腾</span>
                </div>
                <div class="row2">
                  <span>🗓️ {{ formatDate(n.free_up_date) }}</span>
                  <span v-if="n.box_id">· 格子 #{{ n.box_id }}</span>
                </div>
                <div class="row3">
                  <span :style="{ color: n.user?.avatar_color }">@{{ n.user?.nickname }}</span>
                  <span v-if="n.description">· {{ n.description }}</span>
                </div>
              </div>
              <div class="item-actions" @click.stop>
                <van-button
                  size="mini"
                  :type="n.is_freed ? 'success' : 'warning'"
                  plain
                  @click="toggleSpaceFreed(n, $event)"
                >
                  {{ n.is_freed ? '撤销' : '释放' }}
                </van-button>
                <van-button
                  size="mini"
                  type="danger"
                  plain
                  @click="deleteSpaceItem(n, $event)"
                >
                  删除
                </van-button>
              </div>
            </div>
          </div>
        </div>
      </van-tab>
    </van-tabs>

    <AppTabbar />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import {
  getSeasonings, getSpaceNotices,
  updateSeasoning, deleteSeasoning,
  updateSpaceNotice, deleteSpaceNotice,
} from '@/api/shared'
import { showToast, showConfirmDialog } from 'vant'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const activeTab = ref('seasoning')
const seasonings = ref([])
const spaces = ref([])

const formatDate = (d) => dayjs(d).format('M月D日')

const isNearExpiry = (d) => {
  if (!d) return false
  return dayjs(d).diff(dayjs(), 'day') <= 7
}

const isPastDate = (d) => dayjs(d).isBefore(dayjs().endOf('day'))

const loadData = async () => {
  try {
    const [s, sp] = await Promise.all([
      getSeasonings({ include_depleted: true }),
      getSpaceNotices({ include_freed: true }),
    ])
    seasonings.value = s
    spaces.value = sp
  } catch (e) {}
}

const openSeasoningForm = (item = null) => {
  if (!item) {
    router.push('/seasoning/add')
  } else {
    router.push({
      path: `/seasoning/edit/${item.id}`,
      params: { data: encodeURIComponent(JSON.stringify(item)) },
    })
  }
}

const openSpaceForm = (item = null) => {
  if (!item) {
    router.push('/space-notice/add')
  } else {
    router.push({
      path: `/space-notice/edit/${item.id}`,
      params: { data: encodeURIComponent(JSON.stringify(item)) },
    })
  }
}

const toggleSeasoningDepleted = async (item, e) => {
  e.stopPropagation()
  try {
    await updateSeasoning(item.id, { is_depleted: !item.is_depleted })
    showToast(item.is_depleted ? '已恢复' : '已标记用完')
    loadData()
  } catch (err) {}
}

const toggleSpaceFreed = async (item, e) => {
  e.stopPropagation()
  try {
    await updateSpaceNotice(item.id, { is_freed: !item.is_freed })
    showToast(item.is_freed ? '已撤销释放' : '已标记已释放')
    loadData()
  } catch (err) {}
}

const deleteSeasoningItem = async (item, e) => {
  e.stopPropagation()
  try {
    await showConfirmDialog({ title: '删除确认', message: `确定删除「${item.name}」？` })
    await deleteSeasoning(item.id)
    showToast('已删除')
    loadData()
  } catch (err) {}
}

const deleteSpaceItem = async (item, e) => {
  e.stopPropagation()
  try {
    await showConfirmDialog({ title: '删除确认', message: '确定删除这条预告？' })
    await deleteSpaceNotice(item.id)
    showToast('已删除')
    loadData()
  } catch (err) {}
}

onMounted(loadData)
</script>

<style lang="less" scoped>
.page-header {
  .header-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }

  .header-title {
    flex: 1;
    min-width: 0;
  }

  .user-avatar {
    width: 44px;
    height: 44px;
    border-radius: 14px;
    color: #fff;
    font-size: 20px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    cursor: pointer;
    transition: transform 0.2s;

    &:active {
      transform: scale(0.92);
    }
  }
}

.list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #fafafa;
  border-radius: 12px;

  &.depleted, &.freed {
    opacity: 0.6;
    background: #f2f3f5;
  }

  .avatar {
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

  .content {
    flex: 1;
    min-width: 0;
  }

  .row1 {
    display: flex;
    align-items: center;
    gap: 8px;

    .name {
      font-size: 15px;
      font-weight: 600;
      color: #323233;
    }

    .tag-exp {
      background: #f2f3f5;
      color: #969799;
      padding: 1px 8px;
      border-radius: 10px;
      font-size: 11px;
    }

    .tag-warn {
      background: #fff3e8;
      color: #ff976a;
      padding: 1px 8px;
      border-radius: 10px;
      font-size: 11px;
    }
  }

  .row2, .row3 {
    font-size: 12px;
    color: #969799;
    margin-top: 3px;
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }

  .item-actions {
    display: flex;
    flex-direction: column;
    gap: 6px;
    flex-shrink: 0;
  }
}
</style>
