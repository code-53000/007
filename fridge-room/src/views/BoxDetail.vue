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
            <span v-if="box.box_status === 'grace'" class="badge grace">宽限期</span>
            <span v-else-if="box.box_status === 'released'" class="badge released">已释放</span>
            <span v-else-if="box.box_status === 'expiring'" class="badge expiring">即将到期</span>
          </p>
          <p v-if="box.description" class="desc">{{ box.description }}</p>
          <p v-if="!box.is_public && box.expires_at" class="desc expiry-info">
            <template v-if="box.box_status === 'grace'">
              ⚠️ 已过期，宽限期至 {{ formatDate(box.expires_at) }}，请尽快取出食物
            </template>
            <template v-else-if="box.box_status === 'released'">
              ⛔ 宽限期已过，格子即将被释放
            </template>
            <template v-else>
              🕐 有效期至 {{ formatDate(box.expires_at) }}
            </template>
          </p>
        </div>
      </div>

      <div v-if="box.box_status === 'grace'" class="expiry-warning-bar">
        ⚠️ 此格子已过期，处于宽限期中。你可以取出食物，但不能放入新食物。
      </div>
      <div v-else-if="box.box_status === 'released'" class="expiry-warning-bar danger">
        ⛔ 此格子宽限期已过，即将被系统释放，请立即取出食物！
      </div>

      <div class="card">
        <div class="section-title">
          <span>格子里的食物 ({{ activeFoods.length }})</span>
          <van-button
            v-if="box.box_status !== 'grace' && box.box_status !== 'released'"
            size="small"
            type="primary"
            @click="$router.push(`/food/add?box_id=${box.id}`)"
          >
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

    <van-dialog
      v-model:show="showEdit"
      title="编辑格子"
      show-cancel-button
      @confirm="onSaveBox"
      :confirm-button-text="isOwner ? '保存' : '确定'"
      :show-confirm-button="isOwner"
      :show-cancel-button="isOwner"
    >
      <div class="edit-form" v-if="box">
        <van-form>
          <van-cell-group inset>
            <van-field
              v-model="editForm.name"
              label="格子名称"
              placeholder="请输入格子名称"
              :readonly="!isOwner"
            />
            <van-field label="所在层" :readonly="!isOwner">
              <template #input>
                <van-stepper v-model="editForm.floor" :min="1" :max="10" input-width="80px" :readonly="!isOwner" :disabled="!isOwner" />
              </template>
            </van-field>
            <van-field label="行号" :readonly="!isOwner">
              <template #input>
                <van-stepper v-model="editForm.row" :min="1" :max="10" input-width="80px" :readonly="!isOwner" :disabled="!isOwner" />
              </template>
            </van-field>
            <van-field label="容量" :readonly="!isOwner">
              <template #input>
                <van-stepper v-model="editForm.capacity" :min="1" :max="100" input-width="80px" :readonly="!isOwner" :disabled="!isOwner" />
                <span class="unit-hint">份</span>
              </template>
            </van-field>
          </van-cell-group>

          <div class="card" style="box-shadow:none">
            <div class="section-title" style="margin: 16px 4px 8px">🔒 权限</div>
            <van-cell-group inset>
              <van-cell center title="设为公共格子" :readonly="!isOwner">
                <template #right-icon>
                  <van-switch v-model="editForm.is_public" :disabled="!isOwner" />
                </template>
              </van-cell>
            </van-cell-group>
          </div>

          <div class="card" style="box-shadow:none">
            <div class="section-title" style="margin: 16px 4px 8px">📝 备注</div>
            <van-cell-group inset>
              <van-field
                v-model="editForm.description"
                rows="2"
                autosize
                label="描述"
                type="textarea"
                placeholder="填写格子描述"
                :readonly="!isOwner"
              />
            </van-cell-group>
          </div>
        </van-form>

        <div v-if="isOwner" class="delete-btn-wrap">
          <van-button block type="danger" plain @click="onDeleteBox">
            删除格子
          </van-button>
        </div>
      </div>
    </van-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showConfirmDialog, showToast, showDialog } from 'vant'
import { getBoxDetail, updateBox, deleteBox } from '@/api/boxes'
import { cleanupFood, deleteFood } from '@/api/foods'
import { useUserStore } from '@/stores/user'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const boxId = computed(() => route.params.id)
const box = ref(null)
const actionSheet = ref(false)
const currentFood = ref(null)
const showEdit = ref(false)

const editForm = reactive({
  name: '',
  floor: 1,
  row: 1,
  capacity: 10,
  is_public: false,
  description: '',
})

const isOwner = computed(() => box.value?.owner_id === userStore.userId)

const activeFoods = computed(() => box.value?.foods || [])

const actions = computed(() => {
  const list = [
    { name: '查看详情', action: 'detail' },
    { name: '标记已清理', action: 'cleanup' },
  ]
  if (currentFood.value?.owner_id === userStore.userId) {
    list.splice(1, 0, { name: '编辑食物', action: 'edit' })
  }
  list.push({ name: '删除记录', action: 'delete', color: '#ee0a24' })
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

const formatDate = (d) => dayjs(d).format('M/D')

const loadData = async () => {
  try {
    box.value = await getBoxDetail(boxId.value)
  } catch (e) {}
}

const fillEditForm = () => {
  if (!box.value) return
  editForm.name = box.value.name || ''
  editForm.floor = box.value.floor || 1
  editForm.row = box.value.row || 1
  editForm.capacity = box.value.capacity || 10
  editForm.is_public = box.value.is_public || false
  editForm.description = box.value.description || ''
}

watch(showEdit, (v) => {
  if (v) fillEditForm()
})

const onSaveBox = async () => {
  if (!isOwner.value) return true
  if (!editForm.name.trim()) {
    showToast('请填写格子名称')
    return false
  }
  try {
    await updateBox(boxId.value, {
      name: editForm.name,
      floor: editForm.floor,
      row: editForm.row,
      capacity: editForm.capacity,
      is_public: editForm.is_public,
      description: editForm.description,
    })
    showToast('保存成功')
    showEdit.value = false
    await loadData()
  } catch (e) {
    showToast(e?.response?.data?.detail || '保存失败，请重试')
    return false
  }
}

const onDeleteBox = async () => {
  try {
    await showConfirmDialog({
      title: '删除格子',
      message: `确定删除「${box.value?.name}」吗？格子内的食物记录也会被清除，此操作不可恢复。`,
      confirmButtonText: '删除',
      confirmButtonColor: '#ee0a24',
    })
    await deleteBox(boxId.value)
    showToast('已删除')
    router.replace('/')
  } catch (e) {}
}

const showFoodMenu = (f) => {
  currentFood.value = f
  actionSheet.value = true
}

const handleAction = async (a) => {
  if (!currentFood.value) return
  const f = currentFood.value

  if (a.action === 'edit') {
    router.push(`/food/edit/${f.id}`)
    actionSheet.value = false
  } else if (a.action === 'cleanup') {
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

        &.grace {
          background: #ff976a;
        }

        &.released {
          background: #969799;
        }

        &.expiring {
          background: #ff976a;
        }
      }

      &.desc {
        margin-top: 6px;
        color: #969799;

        &.expiry-info {
          color: #ff976a;
        }
      }
    }
  }
}

.expiry-warning-bar {
  margin: 0 16px;
  padding: 10px 14px;
  background: #fff3e8;
  border-radius: 8px;
  font-size: 13px;
  color: #ff976a;
  font-weight: 500;

  &.danger {
    background: #fde8e8;
    color: #ee0a24;
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

.edit-form {
  padding: 4px 0 12px;

  .unit-hint {
    margin-left: 8px;
    font-size: 13px;
    color: #969799;
  }

  .section-title {
    font-size: 13px;
    color: #969799;
    padding: 0 16px;
  }
}

.delete-btn-wrap {
  padding: 20px 20px 4px;
}
</style>
