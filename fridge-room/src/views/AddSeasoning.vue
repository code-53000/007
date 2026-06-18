<template>
  <div class="page-container">
    <van-nav-bar
      :title="isEdit ? '编辑调料' : '添加调料'"
      left-arrow
      @click-left="$router.back()"
      fixed
      placeholder
    />

    <van-form @submit="onSubmit" class="form-wrap">
      <div class="card">
        <div class="section-title">🧂 基本信息</div>
        <van-cell-group inset>
          <van-field
            v-model="form.name"
            label="名称"
            placeholder="如：生抽、老干妈"
            required
          />
          <van-field
            v-model="form.brand"
            label="品牌"
            placeholder="如：海天（选填）"
          />
          <van-field
            v-model="form.category"
            is-link
            readonly
            label="分类"
            required
            @click="showCatPicker = true"
          >
            <template #input>
              <span v-if="form.category" class="val">{{ form.category }}</span>
            </template>
          </van-field>
          <van-field
            v-model="form.quantity"
            label="数量"
            placeholder="如：1瓶、半瓶（选填）"
          />
        </van-cell-group>
      </div>

      <div class="card">
        <div class="section-title">📍 位置与保质期</div>
        <van-cell-group inset>
          <van-field
            v-model="form.location_note"
            label="存放位置"
            placeholder="如：冰箱门第二层（选填）"
          />
          <van-field
            v-model="expiryDateStr"
            type="date"
            label="过期日期"
            @update:model-value="updateExpiryDate"
          />
        </van-cell-group>
      </div>

      <div v-if="isEdit" class="card">
        <div class="section-title">🔄 状态</div>
        <van-cell-group inset>
          <van-cell center title="标记为已用完">
            <template #right-icon>
              <van-switch v-model="form.is_depleted" />
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
          删除此调料
        </van-button>
        <van-button round block type="primary" native-type="submit" :loading="loading">
          {{ isEdit ? '保存修改' : '添加调料' }}
        </van-button>
      </div>
    </van-form>

    <van-popup v-model:show="showCatPicker" round position="bottom">
      <van-picker
        :columns="categoryOptions"
        title="选择分类"
        @confirm="onCatConfirm"
        @cancel="showCatPicker = false"
      />
    </van-popup>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast, showConfirmDialog } from 'vant'
import dayjs from 'dayjs'
import {
  createSeasoning,
  updateSeasoning,
  deleteSeasoning,
} from '@/api/shared'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const deleting = ref(false)
const showCatPicker = ref(false)
const seasoningId = computed(() => route.params.id)
const isEdit = computed(() => !!seasoningId.value)

const categories = ['调味', '酱料', '食用油', '香料', '干货', '其他']
const categoryOptions = categories.map(c => ({ text: c, value: c }))

const form = reactive({
  name: '',
  brand: '',
  category: '调味',
  quantity: '',
  location_note: '',
  expiry_date: null,
  is_depleted: false,
})

const expiryDateStr = ref('')

const updateExpiryDate = (val) => {
  if (val) {
    form.expiry_date = dayjs(val).format('YYYY-MM-DD')
  } else {
    form.expiry_date = null
  }
}

const onCatConfirm = ({ selectedOptions }) => {
  form.category = selectedOptions[0].value
  showCatPicker.value = false
}

const onSubmit = async () => {
  if (!form.name.trim()) return showToast('请填写调料名称')

  loading.value = true
  try {
    const payload = { ...form }
    if (!payload.brand) delete payload.brand
    if (!payload.quantity) delete payload.quantity
    if (!payload.location_note) delete payload.location_note
    if (!payload.expiry_date) delete payload.expiry_date
    if (!isEdit.value) delete payload.is_depleted

    if (isEdit.value) {
      await updateSeasoning(seasoningId.value, payload)
      showToast('修改成功')
    } else {
      await createSeasoning(payload)
      showToast('添加成功')
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
      message: `确定删除「${form.name}」？`,
    })
    deleting.value = true
    await deleteSeasoning(seasoningId.value)
    showToast('已删除')
    router.back()
  } catch (e) {
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  if (isEdit.value && route.params.data) {
    const data = JSON.parse(decodeURIComponent(route.params.data))
    Object.assign(form, {
      name: data.name || '',
      brand: data.brand || '',
      category: data.category || '调味',
      quantity: data.quantity || '',
      location_note: data.location_note || '',
      expiry_date: data.expiry_date || null,
      is_depleted: data.is_depleted || false,
    })
    if (form.expiry_date) {
      expiryDateStr.value = dayjs(form.expiry_date).format('YYYY-MM-DD')
    }
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
</style>
