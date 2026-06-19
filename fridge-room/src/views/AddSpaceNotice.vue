<template>
  <div class="page-container">
    <van-nav-bar
      :title="isEdit ? '编辑预告' : '发布空间预告'"
      left-arrow
      @click-left="$router.back()"
      fixed
      placeholder
    />

    <van-form @submit="onSubmit" class="form-wrap">
      <div class="card">
        <div class="section-title">📦 空间信息</div>
        <van-cell-group inset>
          <van-field
            v-model="form.space_size"
            label="空间大小"
            placeholder="如：一个格子、半层（选填）"
          />
          <van-field
            v-model="freeUpDateStr"
            type="date"
            label="释放日期"
            placeholder="选择预计腾出的日期"
            required
            @update:model-value="updateFreeUpDate"
          />
          <van-field
            v-model="selectedBoxName"
            is-link
            readonly
            label="关联格子"
            placeholder="选择要腾出的格子（选填）"
            @click="showBoxPicker = true"
          >
            <template #input>
              <span v-if="selectedBoxName" class="val">{{ selectedBoxName }}</span>
            </template>
            <template #right-icon>
              <van-icon
                v-if="form.box_id"
                name="clear"
                @click.stop="clearBox"
              />
            </template>
          </van-field>
        </van-cell-group>
      </div>

      <div class="card">
        <div class="section-title">📝 补充说明</div>
        <van-cell-group inset>
          <van-field
            v-model="form.description"
            rows="3"
            autosize
            label="描述"
            type="textarea"
            placeholder="如：周末会清理，里面的东西可以用"
            maxlength="200"
            show-word-limit
          />
        </van-cell-group>
      </div>

      <div v-if="isEdit" class="card">
        <div class="section-title">🔄 状态</div>
        <van-cell-group inset>
          <van-cell center title="标记为已释放">
            <template #right-icon>
              <van-switch v-model="form.is_freed" />
            </template>
          </van-cell>
        </van-cell-group>
      </div>

      <div class="form-submit">
        <van-button
          v-if="isEdit"
          round
          block
          type="danger"
          plain
          :loading="deleting"
          style="margin-bottom: 12px"
          @click="onDelete"
        >
          删除此预告
        </van-button>
        <van-button round block type="primary" native-type="submit" :loading="loading">
          {{ isEdit ? '保存修改' : '发布预告' }}
        </van-button>
      </div>
    </van-form>

    <van-popup v-model:show="showBoxPicker" round position="bottom" style="max-height: 60%">
      <div class="picker-title">选择我的格子</div>
      <van-cell-group v-if="!boxes.length">
        <van-empty description="暂无我的格子" />
      </van-cell-group>
      <div v-else class="box-picker-list">
        <div
          v-for="b in boxes"
          :key="b.id"
          class="box-picker-item"
          :class="{ active: Number(form.box_id) === Number(b.id) }"
          @click="selectBox(b)"
        >
          <span class="avatar" :style="{ background: b.owner?.avatar_color || '#c8c9cc' }">
            {{ b.owner?.nickname?.[0] || '?' }}
          </span>
          <div class="meta">
            <div class="name">{{ b.name }}</div>
            <div class="sub">第{{ b.floor }}层 · {{ b.owner?.nickname }}</div>
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showConfirmDialog } from 'vant'
import dayjs from 'dayjs'
import {
  createSpaceNotice,
  updateSpaceNotice,
  deleteSpaceNotice,
  getSpaceNotice,
} from '@/api/shared'
import { getBoxes } from '@/api/boxes'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const deleting = ref(false)
const showBoxPicker = ref(false)
const boxes = ref([])
const noticeId = computed(() => route.params.id)
const isEdit = computed(() => !!noticeId.value)

const form = reactive({
  box_id: null,
  free_up_date: null,
  description: '',
  space_size: '',
  is_freed: false,
})

const freeUpDateStr = ref('')

const selectedBoxName = computed(() => {
  const b = boxes.value.find(x => Number(x.id) === Number(form.box_id))
  return b ? b.name : ''
})

const updateFreeUpDate = (val) => {
  if (val) {
    form.free_up_date = dayjs(val).format('YYYY-MM-DD')
  } else {
    form.free_up_date = null
  }
}

const selectBox = (b) => {
  form.box_id = b.id
  showBoxPicker.value = false
}

const clearBox = () => {
  form.box_id = null
}

const loadMyBoxes = async () => {
  try {
    boxes.value = await getBoxes({ owner_id: userStore.userId })
  } catch (e) {
    showToast('加载格子列表失败')
  }
}

const loadDetail = async () => {
  if (!isEdit.value) return
  try {
    const data = await getSpaceNotice(noticeId.value)
    Object.assign(form, {
      box_id: data.box_id || null,
      free_up_date: data.free_up_date || null,
      description: data.description || '',
      space_size: data.space_size || '',
      is_freed: data.is_freed || false,
    })
    if (form.free_up_date) {
      freeUpDateStr.value = dayjs(form.free_up_date).format('YYYY-MM-DD')
    }
  } catch (e) {
    showToast('加载失败')
  }
}

const onSubmit = async () => {
  if (!form.free_up_date) return showToast('请选择释放日期')

  loading.value = true
  try {
    const payload = { ...form }
    if (!payload.box_id) payload.box_id = null
    if (!payload.description) delete payload.description
    if (!payload.space_size) delete payload.space_size
    if (!isEdit.value) delete payload.is_freed

    if (isEdit.value) {
      await updateSpaceNotice(noticeId.value, payload)
      showToast('修改成功')
    } else {
      await createSpaceNotice(payload)
      showToast('发布成功')
    }
    router.back()
  } catch (e) {
  } finally {
    loading.value = false
  }
}

const onDelete = async () => {
  try {
    await showConfirmDialog({
      title: '删除确认',
      message: '确定删除这条空间预告？',
    })
    deleting.value = true
    await deleteSpaceNotice(noticeId.value)
    showToast('已删除')
    router.back()
  } catch (e) {
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  await loadMyBoxes()
  await loadDetail()
  if (!isEdit.value) {
    freeUpDateStr.value = dayjs().add(1, 'day').format('YYYY-MM-DD')
    updateFreeUpDate(freeUpDateStr.value)
  }
})
</script>

<style lang="less" scoped>
.form-wrap {
  padding-bottom: 40px;
}

.val {
  color: #323233 !important;
}

.form-submit {
  padding: 16px 20px;
  position: sticky;
  bottom: 0;
  background: #f7f8fa;
  z-index: 10;
}

.picker-title {
  padding: 14px;
  text-align: center;
  font-weight: 600;
  font-size: 16px;
  border-bottom: 1px solid #ebedf0;
}

.box-picker-list {
  max-height: 400px;
  overflow-y: auto;
  padding: 8px;
}

.box-picker-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 10px;
  margin-bottom: 6px;
  background: #f7f8fa;

  &.active {
    background: #e8f3ff;
  }

  .avatar {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    flex-shrink: 0;
  }

  .name {
    font-weight: 600;
    font-size: 15px;
  }

  .sub {
    font-size: 12px;
    color: #969799;
    margin-top: 2px;
  }
}
</style>
