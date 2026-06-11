<template>
  <div class="page-container">
    <div class="page-header">
      <h1>🧊 冰箱格子</h1>
      <div class="subtitle">{{ stats.available_boxes }} 个可用 / 共 {{ stats.total_boxes }} 个</div>
    </div>

    <div class="stats-card card">
      <div class="stat-item" v-for="s in statItems" :key="s.label">
        <div class="stat-val" :style="{ color: s.color }">{{ s.value }}</div>
        <div class="stat-label">{{ s.label }}</div>
      </div>
    </div>

    <div class="card">
      <div class="section-title">
        <span>格子列表</span>
        <van-button size="small" type="primary" plain @click="$router.push('/box/add')">
          + 新建
        </van-button>
      </div>

      <van-tabs v-model:active="activeFloor" sticky>
        <van-tab
          v-for="n in Math.max(totalFloors, 3)"
          :key="n"
          :title="`第${n}层`"
          :name="n"
        >
          <div v-if="currentFloorBoxes.length === 0" class="empty-state">
            <div class="empty-icon">📭</div>
            <div class="empty-text">这层还没有格子</div>
          </div>

          <div class="box-grid">
            <div
              v-for="box in currentFloorBoxes"
              :key="box.id"
              class="box-card"
              @click="$router.push(`/box/${box.id}`)"
            >
              <div class="box-head" :style="{ background: box.owner?.avatar_color || '#c8c9cc' }">
                <span v-if="box.is_public" class="tag-pub">公</span>
                <span v-else class="box-letter">{{ box.owner?.nickname?.[0] || '?' }}</span>
              </div>
              <div class="box-body">
                <div class="box-name">{{ box.name }}</div>
                <div class="box-meta">
                  <span class="owner">{{ box.owner?.nickname || '未分配' }}</span>
                  <span class="count">{{ box.food_count }} 件</span>
                </div>
                <div class="capacity-bar">
                  <div
                    class="capacity-fill"
                    :style="{
                      width: `${Math.min((box.used_capacity / (box.capacity || 10)) * 100, 100)}%`,
                      background: box.used_capacity >= box.capacity ? '#ee0a24' : '#07c160'
                    }"
                  />
                </div>
              </div>
            </div>
          </div>
        </van-tab>
      </van-tabs>
    </div>

    <van-fab
      :show="true"
      type="primary"
      icon="plus"
      @click="$router.push('/food/add')"
      text="登记食物"
    />

    <AppTabbar />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getBoxes, getBoxStats } from '@/api/boxes'

const boxes = ref([])
const stats = ref({
  total_boxes: 0,
  public_boxes: 0,
  private_boxes: 0,
  occupied_boxes: 0,
  available_boxes: 0,
  total_floors: 0,
})
const activeFloor = ref(1)

const statItems = computed(() => [
  { label: '总格子', value: stats.value.total_boxes, color: '#1989fa' },
  { label: '公共', value: stats.value.public_boxes, color: '#07c160' },
  { label: '私有', value: stats.value.private_boxes, color: '#7232dd' },
  { label: '可用', value: stats.value.available_boxes, color: '#ff976a' },
])

const totalFloors = computed(() => {
  if (!boxes.value.length) return 3
  return Math.max(...boxes.value.map(b => b.floor))
})

const currentFloorBoxes = computed(() => {
  return boxes.value.filter(b => b.floor === activeFloor.value)
})

const loadData = async () => {
  try {
    const [list, s] = await Promise.all([getBoxes(), getBoxStats()])
    boxes.value = list
    stats.value = s
  } catch (e) {}
}

onMounted(loadData)
</script>

<style lang="less" scoped>
.stats-card {
  display: flex;
  justify-content: space-around;
  padding: 16px;

  .stat-item {
    text-align: center;

    .stat-val {
      font-size: 24px;
      font-weight: 700;
      line-height: 1;
    }

    .stat-label {
      font-size: 12px;
      color: #969799;
      margin-top: 6px;
    }
  }
}

.box-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 8px 4px;
}

.box-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);

  .box-head {
    height: 52px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-weight: 600;
    position: relative;

    .tag-pub {
      width: 30px;
      height: 30px;
      border-radius: 50%;
      background: rgba(255,255,255,0.25);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 16px;
    }

    .box-letter {
      font-size: 24px;
    }
  }

  .box-body {
    padding: 10px 12px;

    .box-name {
      font-size: 15px;
      font-weight: 600;
      color: #323233;
    }

    .box-meta {
      display: flex;
      justify-content: space-between;
      margin-top: 4px;
      font-size: 12px;
      color: #969799;
    }

    .capacity-bar {
      height: 4px;
      background: #f2f3f5;
      border-radius: 2px;
      margin-top: 8px;
      overflow: hidden;

      .capacity-fill {
        height: 100%;
        border-radius: 2px;
        transition: width 0.3s;
      }
    }
  }
}
</style>
