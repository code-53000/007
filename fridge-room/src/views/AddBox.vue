<template>
  <div class="page-container">
    <van-nav-bar title="新建格子" left-arrow @click-left="$router.back()" fixed placeholder />

    <van-form @submit="onSubmit" class="form-wrap">
      <div class="card">
        <div class="section-title">📍 基本信息</div>
        <van-cell-group inset>
          <van-field
            v-model="form.name"
            label="格子名称"
            placeholder="如：小明的饭盒位、左数第2格"
            required
          />
          <van-field label="所在层">
            <template #input>
              <van-stepper v-model="form.floor" :min="1" :max="10" input-width="80px" />
            </template>
          </van-field>
          <van-field label="行号">
            <template #input>
              <van-stepper v-model="form.row" :min="1" :max="10" input-width="80px" />
            </template>
          </van-field>
          <van-field label="容量">
            <template #input>
              <van-stepper v-model="form.capacity" :min="1" :max="100" input-width="80px" />
              <span class="unit-hint">份</span>
            </template>
          </van-field>
        </van-cell-group>
      </div>

      <div class="card">
        <div class="section-title">🔒 权限</div>
        <van-cell-group inset>
          <van-cell center title="设为公共格子">
            <template #right-icon>
              <van-switch v-model="form.is_public" />
            </template>
          </van-cell>
        </van-cell-group>
        <div class="tip" v-if="form.is_public">
          公共格子：任何人都可以放东西，建议设置短保质期
        </div>
        <div class="tip" v-else>
          私有格子：只有你可以放东西
        </div>
        <div class="limit-info" v-if="!form.is_public">
          <div class="limit-row">
            <span>有效期：{{ boxStats.private_box_expiry_days }} 天</span>
            <span>宽限期：{{ boxStats.private_box_grace_days }} 天</span>
          </div>
          <div class="limit-row">
            <span>你的私有格子：{{ boxStats.user_private_boxes }} / {{ boxStats.max_private_boxes_per_user }}</span>
          </div>
        </div>
      </div>

      <div class="card" v-if="!canCreateAny || !canCreatePrivate">
        <div class="warning-info">
          <span v-if="!canCreateAny">⚠️ 格子总数已满（{{ boxStats.total_boxes }}/{{ boxStats.max_boxes }}），请先清理不用的格子</span>
          <span v-else-if="!canCreatePrivate">⚠️ 你的私有格子已达上限（{{ boxStats.user_private_boxes }}/{{ boxStats.max_private_boxes_per_user }}）</span>
        </div>
      </div>

      <div class="card">
        <div class="section-title">📝 备注（选填）</div>
        <van-cell-group inset>
          <van-field
            v-model="form.description"
            rows="2"
            autosize
            label="描述"
            type="textarea"
            placeholder="例如：这一格专门放盒饭"
          />
        </van-cell-group>
      </div>

      <div class="form-submit">
        <van-button round block type="primary" native-type="submit" :loading="loading">
          创建格子
        </van-button>
      </div>
    </van-form>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { showToast } from 'vant'
import { createBox, getBoxStats } from '@/api/boxes'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const loading = ref(false)
const boxStats = ref({
  total_boxes: 0,
  max_boxes: 50,
  max_private_boxes_per_user: 5,
  user_private_boxes: 0,
  private_box_expiry_days: 7,
  private_box_grace_days: 3,
})

const form = reactive({
  name: '',
  floor: 1,
  row: 1,
  capacity: 10,
  is_public: false,
  description: '',
})

const canCreatePrivate = computed(() => {
  return form.is_public || boxStats.value.user_private_boxes < boxStats.value.max_private_boxes_per_user
})

const canCreateAny = computed(() => {
  return boxStats.value.total_boxes < boxStats.value.max_boxes
})

const loadStats = async () => {
  try {
    boxStats.value = await getBoxStats()
  } catch (e) {}
}

const onSubmit = async () => {
  if (!form.name.trim()) return showToast('请填写格子名称')
  if (!canCreateAny.value) return showToast('格子数量已满，请先清理不用的格子')
  if (!canCreatePrivate.value) return showToast('你的格子数量已达上限')
  loading.value = true
  try {
    const res = await createBox(form)
    showToast('创建成功')
    router.replace(`/box/${res.id}`)
  } catch (e) {
  } finally {
    loading.value = false
  }
}

loadStats()
</script>

<style lang="less" scoped>
.form-wrap {
  padding-bottom: 40px;
}

.tip {
  margin: 12px 20px 0;
  padding: 10px 14px;
  background: #f7f8fa;
  border-radius: 8px;
  font-size: 12px;
  color: #969799;
}

.limit-info {
  margin: 10px 20px 0;
  padding: 10px 14px;
  background: #e8f3ff;
  border-radius: 8px;
  font-size: 12px;
  color: #1989fa;

  .limit-row {
    display: flex;
    justify-content: space-between;
    gap: 8px;

    & + .limit-row {
      margin-top: 4px;
    }
  }
}

.warning-info {
  margin: 12px 20px;
  padding: 10px 14px;
  background: #fff3e8;
  border-radius: 8px;
  font-size: 13px;
  color: #ff976a;
  font-weight: 500;
}

.form-submit {
  padding: 16px 20px;
}

.unit-hint {
  margin-left: 8px;
  font-size: 13px;
  color: #969799;
}
</style>
