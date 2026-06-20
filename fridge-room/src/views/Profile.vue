<template>
  <div class="page-container">
    <div class="page-header" :style="{ background: `linear-gradient(135deg, ${userStore.avatarColor}, #fff)` }">
      <div class="profile-head">
        <div class="avatar" :style="{ background: userStore.avatarColor }">
          {{ userStore.user?.nickname?.[0] || '?' }}
        </div>
        <div class="info">
          <h2>{{ userStore.user?.nickname }}</h2>
          <p>@{{ userStore.user?.username }} · {{ userStore.user?.room_number || '未设置房间' }}</p>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="section-title"><span>📊 我的数据</span></div>
      <div class="mini-stats">
        <div class="mini-item">
          <span class="v">{{ myBoxes }}</span>
          <span class="l">格子</span>
        </div>
        <div class="mini-item">
          <span class="v" style="color:#1989fa">{{ myActiveFoods }}</span>
          <span class="l">在存食物</span>
        </div>
        <div class="mini-item">
          <span class="v" :style="{ color: expiringCount ? '#ee0a24' : '#07c160' }">{{ expiringCount }}</span>
          <span class="l">将到期</span>
        </div>
        <div class="mini-item">
          <span class="v" style="color:#7232dd">{{ cleanupCount }}</span>
          <span class="l">清理次数</span>
        </div>
      </div>
    </div>

    <div class="card">
      <van-cell-group inset>
        <van-cell title="编辑个人信息" is-link icon="edit" @click="openEditProfile" />
        <van-cell title="我的食物" is-link icon="friends-o" to="/my-foods" />
        <van-cell title="清理记录" is-link icon="delete" to="/cleanup" />
        <van-cell title="操作记录" is-link icon="orders-o" to="/logs" />
      </van-cell-group>
    </div>

    <div class="card">
      <div class="section-title">
        <span>👥 室友</span>
        <span class="count">{{ roommates.length }}人</span>
      </div>
      <div class="roommates">
        <div
          v-for="r in roommates"
          :key="r.id"
          class="roommate"
          :class="{ self: r.id === userStore.userId }"
        >
          <div class="avatar" :style="{ background: r.avatar_color }">
            {{ r.nickname?.[0] }}
          </div>
          <span class="nick">{{ r.nickname }}</span>
          <span v-if="r.id === userStore.userId" class="me-tag">我</span>
        </div>
      </div>
    </div>

    <div class="card danger">
      <van-cell-group inset>
        <van-cell
          title="退出登录"
          icon="logout"
          :border="false"
          @click="onLogout"
        >
          <template #title>
            <span style="color:#ee0a24">退出登录</span>
          </template>
        </van-cell>
      </van-cell-group>
    </div>

    <div class="footer">
      🧊 冰箱管家 v1.0 · 让合租更和谐
    </div>

    <AppTabbar />

    <van-dialog v-model:show="showEdit" title="编辑资料" show-cancel-button @confirm="onSaveProfile">
      <div class="edit-form">
        <van-field v-model="editForm.nickname" label="昵称" />
        <van-field v-model="editForm.room_number" label="房间号" />
        <div class="color-picker">
          <div class="lbl">头像颜色</div>
          <div class="colors">
            <div
              v-for="c in colors"
              :key="c"
              class="color-item"
              :class="{ active: editForm.avatar_color === c }"
              :style="{ background: c }"
              @click="editForm.avatar_color = c"
            />
          </div>
        </div>
      </div>
    </van-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, showToast } from 'vant'
import { useUserStore } from '@/stores/user'
import { getBoxes } from '@/api/boxes'
import { getFoods } from '@/api/foods'
import { getCleanupRecords } from '@/api/shared'

const userStore = useUserStore()
const router = useRouter()
const showEdit = ref(false)
const colors = ['#1989fa', '#07c160', '#ff976a', '#ee0a24', '#7232dd', '#606266']

const roommates = computed(() => userStore.roommates)
const myBoxes = ref(0)
const myActiveFoods = ref(0)
const cleanupCount = ref(0)
const expiringCount = ref(0)

const editForm = reactive({
  nickname: '',
  room_number: '',
  avatar_color: colors[0],
})

const openEditProfile = () => {
  editForm.nickname = userStore.user?.nickname || ''
  editForm.room_number = userStore.user?.room_number || ''
  editForm.avatar_color = userStore.user?.avatar_color || colors[0]
  showEdit.value = true
}

const onSaveProfile = async () => {
  if (!editForm.nickname.trim()) {
    showToast('昵称不能为空')
    return false
  }
  await userStore.updateUser({
    nickname: editForm.nickname,
    room_number: editForm.room_number,
    avatar_color: editForm.avatar_color,
  })
  showEdit.value = false
}

const onLogout = async () => {
  try {
    await showConfirmDialog({
      title: '退出登录',
      message: '确定要退出登录吗？',
    })
    userStore.logout()
    router.replace('/login')
  } catch (e) {}
}

const loadData = async () => {
  try {
    await userStore.fetchRoommates()
    const [boxes, foods, recs] = await Promise.all([
      getBoxes(),
      getFoods({ owner_id: userStore.userId }),
      getCleanupRecords({ operator_id: userStore.userId }),
    ])
    myBoxes.value = boxes.filter(b => b.owner_id === userStore.userId).length
    const activeFoods = foods.filter(f => !f.is_cleaned)
    myActiveFoods.value = activeFoods.length
    expiringCount.value = activeFoods.filter(f => 
      f.expiry_status === '即将到期' || f.expiry_status === '临期'
    ).length
    cleanupCount.value = recs.length
  } catch (e) {}
}

onMounted(loadData)
</script>

<style lang="less" scoped>
.profile-head {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 0;

  .avatar {
    width: 64px;
    height: 64px;
    border-radius: 18px;
    color: #fff;
    font-size: 30px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  }

  h2 {
    font-size: 22px;
    color: #323233;
    margin-bottom: 4px;
  }

  p {
    font-size: 13px;
    color: #646566;
  }
}

.mini-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);

  .mini-item {
    text-align: center;
    padding: 8px 0;

    .v {
      display: block;
      font-size: 22px;
      font-weight: 700;
      color: #323233;
    }

    .l {
      font-size: 12px;
      color: #969799;
      margin-top: 2px;
    }
  }
}

.roommates {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 4px 0;

  .roommate {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    width: 64px;
    position: relative;

    .avatar {
      width: 48px;
      height: 48px;
      border-radius: 14px;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      font-size: 18px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }

    .nick {
      font-size: 12px;
      color: #323233;
      text-align: center;
      max-width: 64px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .me-tag {
      position: absolute;
      top: -4px;
      right: 0;
      background: #1989fa;
      color: #fff;
      font-size: 10px;
      padding: 1px 6px;
      border-radius: 8px;
    }

    &.self {
      .avatar {
        box-shadow: 0 0 0 2px #1989fa;
      }
    }
  }
}

.count {
  font-size: 12px;
  color: #969799;
  font-weight: normal;
}

.danger {
  margin-bottom: 80px;
}

.footer {
  text-align: center;
  padding: 20px;
  font-size: 12px;
  color: #c8c9cc;
}

.edit-form {
  padding: 12px 16px 0;

  .color-picker {
    margin-top: 16px;

    .lbl {
      font-size: 13px;
      color: #969799;
      margin-bottom: 8px;
    }

    .colors {
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }

    .color-item {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      border: 3px solid transparent;
      transition: all 0.2s;

      &.active {
        border-color: #fff;
        box-shadow: 0 0 0 2px #323233;
      }
    }
  }
}
</style>
