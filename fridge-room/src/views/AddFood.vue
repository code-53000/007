<template>
  <div class="page-container">
    <van-nav-bar
      :title="isEdit ? '编辑食物' : '登记食物'"
      left-arrow
      @click-left="$router.back()"
      fixed
      placeholder
    />

    <van-form @submit="onSubmit" class="form-wrap">
      <div class="card">
        <div class="section-title">📦 放到哪里</div>
        <van-cell-group inset>
          <van-field
            v-model="form.box_id"
            is-link
            readonly
            label="选择格子"
            placeholder="请选择要放入的格子"
            required
            @click="showBoxPicker = true"
          >
            <template #input>
              <span v-if="selectedBoxName" class="val">{{ selectedBoxName }}</span>
            </template>
          </van-field>
        </van-cell-group>
      </div>

      <div class="card">
        <div class="section-title">🍱 食物信息</div>
        <van-cell-group inset>
          <van-field
            v-model="form.name"
            label="名称"
            placeholder="如：西红柿、剩下的红烧肉"
            required
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
            v-model.number="form.quantity"
            type="number"
            label="数量"
            required
          />
          <van-field
            v-model="form.unit"
            label="单位"
            placeholder="份/个/克/瓶..."
          />
        </van-cell-group>
      </div>

      <div class="card">
        <div class="section-title">⏰ 保质提醒</div>
        <van-cell-group inset>
          <van-field
            v-model="storedAtStr"
            type="datetime-local"
            label="放入时间"
            @update:model-value="updateStoredAt"
          />
          <van-field label="保质天数">
            <template #input>
              <van-stepper
                v-model="form.expiry_days"
                :min="1"
                :max="365"
                input-width="80px"
              />
            </template>
          </van-field>
        </van-cell-group>

        <div class="expiry-preview" v-if="expiryPreview">
          <div class="preview-label">预计到期：</div>
          <div class="preview-date" :style="{ color: expiryColor }">
            {{ expiryPreview }} · 剩余 {{ remainingDays }} 天
          </div>
        </div>
      </div>

      <div class="card">
        <div class="section-title">📝 备注（选填）</div>
        <van-cell-group inset>
          <van-field
            v-model="form.notes"
            rows="2"
            autosize
            label="备注"
            type="textarea"
            placeholder="如：谁吃了请告诉我~"
            maxlength="200"
            show-word-limit
          />
        </van-cell-group>
      </div>

      <div class="form-submit">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          {{ isEdit ? '保存修改' : '放入冰箱' }}
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

    <van-popup v-model:show="showBoxPicker" round position="bottom" style="max-height: 60%">
      <div class="picker-title">选择格子</div>
      <van-cell-group v-if="!boxes.length">
        <van-empty description="暂无可用格子" />
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
            <div class="sub">第{{ b.floor }}层 · {{ b.owner?.nickname }} · {{ b.food_count }}件</div>
          </div>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showToast } from 'vant'
import dayjs from 'dayjs'
import { createFood, updateFood, getFoodDetail } from '@/api/foods'
import { getBoxes } from '@/api/boxes'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const showBoxPicker = ref(false)
const showCatPicker = ref(false)
const boxes = ref([])
const foodId = computed(() => route.params.id)
const isEdit = computed(() => !!foodId.value)

const categories = ['蔬菜', '水果', '肉类', '蛋奶', '主食', '饮料', '调料', '剩菜', '其他']
const categoryOptions = categories.map(c => ({ text: c, value: c }))

const form = reactive({
  box_id: null,
  name: '',
  category: '其他',
  quantity: 1,
  unit: '份',
  expiry_days: 7,
  notes: '',
})

const storedAtStr = ref(dayjs().format('YYYY-MM-DDTHH:mm'))

const updateStoredAt = (val) => {
  if (val) form.stored_at = dayjs(val).toISOString()
}

watch(() => form.box_id, async () => {
  const b = boxes.value.find(x => Number(x.id) === Number(form.box_id))
  if (b && b.is_public) {
    form.expiry_days = 5
  } else {
    form.expiry_days = 7
  }
})

const expiryPreview = computed(() => {
  const d = dayjs(form.stored_at || new Date()).add(form.expiry_days, 'day')
  return d.format('YYYY年M月D日')
})

const remainingDays = computed(() => {
  const target = dayjs(form.stored_at || new Date()).add(form.expiry_days, 'day')
  return target.diff(dayjs(), 'day')
})

const expiryColor = computed(() => {
  const d = remainingDays.value
  if (d <= 0) return '#969799'
  if (d <= 1) return '#ee0a24'
  if (d <= 3) return '#ff976a'
  return '#07c160'
})

const selectedBoxName = computed(() => {
  const b = boxes.value.find(x => Number(x.id) === Number(form.box_id))
  return b ? b.name : ''
})

const loadBoxes = async () => {
  boxes.value = await getBoxes()
  const qid = route.query.box_id
  if (qid && !form.box_id) {
    form.box_id = Number(qid)
  }
}

const onCatConfirm = ({ selectedOptions }) => {
  form.category = selectedOptions[0].value
  showCatPicker.value = false
}

const selectBox = (b) => {
  form.box_id = b.id
  showBoxPicker.value = false
}

const onSubmit = async () => {
  if (!form.box_id) return showToast('请选择格子')
  if (!form.name.trim()) return showToast('请填写食物名称')

  loading.value = true
  try {
    const payload = { ...form }
    if (!form.stored_at) payload.stored_at = dayjs().toISOString()

    if (isEdit.value) {
      await updateFood(foodId.value, payload)
      showToast('修改成功')
    } else {
      await createFood(payload)
      showToast('放入成功')
    }
    router.back()
  } catch (e) {
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadBoxes()
  if (isEdit.value) {
    try {
      const data = await getFoodDetail(foodId.value)
      Object.assign(form, {
        box_id: data.box_id,
        name: data.name,
        category: data.category,
        quantity: data.quantity,
        unit: data.unit,
        expiry_days: data.expiry_days,
        notes: data.notes,
        stored_at: data.stored_at,
      })
      storedAtStr.value = dayjs(data.stored_at).format('YYYY-MM-DDTHH:mm')
    } catch (e) {}
  } else {
    updateStoredAt(storedAtStr.value)
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

.expiry-preview {
  padding: 12px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;

  .preview-label {
    font-size: 13px;
    color: #969799;
  }

  .preview-date {
    font-size: 14px;
    font-weight: 600;
  }
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
