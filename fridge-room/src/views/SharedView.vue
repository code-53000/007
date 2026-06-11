<template>
  <div class="page-container">
    <div class="page-header" style="background: linear-gradient(135deg, #7232dd, #c39bd3);">
      <h1>🤝 共享空间</h1>
      <div class="subtitle">公共调料 & 即将腾出的空间</div>
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
              <van-icon name="arrow" color="#c8c9cc" />
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
              <van-icon name="arrow" color="#c8c9cc" />
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
import dayjs from 'dayjs'
import {
  getSeasonings, getSpaceNotices,
  createSeasoning, updateSeasoning, deleteSeasoning,
  createSpaceNotice, updateSpaceNotice, deleteSpaceNotice,
} from '@/api/shared'
import { showToast, showConfirmDialog, showDialog } from 'vant'

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

const openSeasoningForm = async (item = null) => {
  if (!item) {
    showDialog({
      title: '功能提示',
      message: '请使用表单添加调料。完整功能可在部署后使用弹窗或路由实现。',
    })
  } else {
    try {
      await showConfirmDialog({
        title: `调料：${item.name}`,
        message: '点击【确认】切换用完状态，或【取消】后点其他区域查看详情。',
        confirmButtonText: item.is_depleted ? '恢复' : '标记用完',
        cancelButtonText: '删除',
      })
      await updateSeasoning(item.id, { is_depleted: !item.is_depleted })
      showToast('更新成功')
      loadData()
    } catch (e) {
      if (e === 'cancel') {
        try {
          await showConfirmDialog({ title: '删除确认', message: `确定删除「${item.name}」？` })
          await deleteSeasoning(item.id)
          showToast('已删除')
          loadData()
        } catch (e2) {}
      }
    }
  }
}

const openSpaceForm = async (item = null) => {
  if (!item) {
    showDialog({
      title: '功能提示',
      message: '请使用表单发布空间预告。完整功能可在部署后使用弹窗或路由实现。',
    })
  } else {
    try {
      await showConfirmDialog({
        title: `空间预告`,
        message: `释放日期：${formatDate(item.free_up_date)}`,
        confirmButtonText: item.is_freed ? '撤销释放' : '标记已释放',
        cancelButtonText: '删除',
      })
      await updateSpaceNotice(item.id, { is_freed: !item.is_freed })
      showToast('更新成功')
      loadData()
    } catch (e) {
      if (e === 'cancel') {
        try {
          await showConfirmDialog({ title: '删除确认', message: '确定删除这条预告？' })
          await deleteSpaceNotice(item.id)
          showToast('已删除')
          loadData()
        } catch (e2) {}
      }
    }
  }
}

onMounted(loadData)
</script>

<style lang="less" scoped>
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
}
</style>
