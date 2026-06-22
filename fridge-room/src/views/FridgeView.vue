<template>
  <div class="page-container">
    <div class="page-header">
      <div class="header-top">
        <div class="header-title">
          <h1>🧊 冰箱格子</h1>
          <div class="subtitle">{{ stats.available_boxes }} 个可用 / 共 {{ stats.total_boxes }} / {{ stats.max_boxes }}</div>
        </div>
        <div class="user-avatar" :style="{ background: userStore.avatarColor }" @click="$router.push('/profile')">
          {{ userStore.user?.nickname?.[0] || '?' }}
        </div>
      </div>
    </div>

    <div class="stats-card card">
      <div class="stat-item" v-for="s in statItems" :key="s.label">
        <div class="stat-val" :style="{ color: s.color }">{{ s.value }}</div>
        <div class="stat-label">{{ s.label }}</div>
      </div>
    </div>

    <div class="card">
      <div class="section-title">
        <div class="title-left">
          <van-tabs v-model:active="viewMode" class="view-tabs" line-width="24px">
            <van-tab title="列表" name="list" />
            <van-tab title="热力" name="heatmap" />
          </van-tabs>
        </div>
        <van-button size="small" type="primary" plain @click="$router.push('/box/add')">
          + 新建
        </van-button>
      </div>

      <div v-if="boxes.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <div class="empty-text">还没有格子，点击右上角新建一个吧~</div>
        <van-button type="primary" size="small" @click="$router.push('/box/add')" style="margin-top: 12px">
          新建格子
        </van-button>
      </div>

      <div v-else>
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

            <div v-else-if="viewMode === 'list'" class="box-grid">
              <div
                v-for="box in currentFloorBoxes"
                :key="box.id"
                class="box-card"
                @click="$router.push(`/box/${box.id}`)"
              >
                <div class="box-head" :style="{ background: box.owner?.avatar_color || '#c8c9cc' }">
                  <span v-if="box.is_public" class="tag-pub">公</span>
                  <span v-else class="box-letter">{{ box.owner?.nickname?.[0] || '?' }}</span>
                  <span v-if="box.box_status === 'grace'" class="tag-expiry grace">宽限期</span>
                  <span v-else-if="box.box_status === 'released'" class="tag-expiry released">已释放</span>
                  <span v-else-if="box.box_status === 'expiring'" class="tag-expiry expiring">即将到期</span>
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

            <div v-else class="heatmap-container">
              <div class="legend">
                <div class="legend-item">
                  <span class="legend-color" style="background: #07c160"></span>
                  <span class="legend-text">空</span>
                </div>
                <div class="legend-item">
                  <span class="legend-color" style="background: #1989fa"></span>
                  <span class="legend-text">正常</span>
                </div>
                <div class="legend-item">
                  <span class="legend-color" style="background: #ff976a"></span>
                  <span class="legend-text">即将到期</span>
                </div>
                <div class="legend-item">
                  <span class="legend-color" style="background: #ee0a24"></span>
                  <span class="legend-text">临期/过期</span>
                </div>
              </div>

              <div class="heatmap-matrix">
                <div
                  v-for="(row, rowIdx) in floorMatrix"
                  :key="rowIdx"
                  class="matrix-row"
                >
                  <div class="row-label">R{{ rowIdx + 1 }}</div>
                  <div class="row-cells" :style="{ gridTemplateColumns: `repeat(${row.length}, 1fr)` }">
                    <div
                      v-for="cell in row"
                      :key="cell.key"
                      class="matrix-cell"
                      :class="[cell.riskClass, { empty: !cell.box }]"
                      @click="cell.box && $router.push(`/box/${cell.box.id}`)"
                    >
                      <template v-if="cell.box">
                        <span class="cell-count">{{ cell.box.food_count }}</span>
                        <span class="cell-name">{{ cell.box.name }}</span>
                      </template>
                      <template v-else>
                        <span class="cell-empty">—</span>
                      </template>
                    </div>
                  </div>
                </div>
              </div>

              <div class="risk-summary">
                <div
                  v-for="item in floorRiskSummary"
                  :key="item.risk"
                  class="risk-item"
                  :class="item.riskClass"
                >
                  <span class="risk-count">{{ item.count }}</span>
                  <span class="risk-label">{{ item.label }}</span>
                </div>
              </div>
            </div>
          </van-tab>
        </van-tabs>
      </div>
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
import { getFoods } from '@/api/foods'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const boxes = ref([])
const foods = ref([])
const stats = ref({
  total_boxes: 0,
  public_boxes: 0,
  private_boxes: 0,
  occupied_boxes: 0,
  available_boxes: 0,
  total_floors: 0,
  max_boxes: 50,
  max_private_boxes_per_user: 5,
  user_private_boxes: 0,
})
const activeFloor = ref(1)
const viewMode = ref('list')

const statusPriority = {
  '已过期': 4,
  '临期': 3,
  '即将到期': 2,
  '正常': 1,
}

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

const boxRiskMap = computed(() => {
  const map = {}
  boxes.value.forEach(box => {
    map[box.id] = { risk: 0, riskClass: 'empty' }
  })
  foods.value.forEach(food => {
    if (!map[food.box_id]) return
    const priority = statusPriority[food.expiry_status] || 0
    if (priority > map[food.box_id].risk) {
      map[food.box_id].risk = priority
    }
  })
  Object.keys(map).forEach(boxId => {
    const item = map[boxId]
    const box = boxes.value.find(b => b.id === parseInt(boxId))
    if (!box || box.food_count === 0) {
      item.riskClass = 'risk-empty'
    } else if (item.risk >= 3) {
      item.riskClass = 'risk-danger'
    } else if (item.risk === 2) {
      item.riskClass = 'risk-warning'
    } else if (item.risk === 1) {
      item.riskClass = 'risk-normal'
    } else {
      item.riskClass = 'risk-empty'
    }
  })
  return map
})

const floorMatrix = computed(() => {
  const floorBoxes = currentFloorBoxes.value
  if (floorBoxes.length === 0) return []

  const rows = {}
  floorBoxes.forEach(box => {
    const row = box.row || 1
    if (!rows[row]) rows[row] = []
    rows[row].push(box)
  })

  const maxRow = Math.max(...Object.keys(rows).map(Number), 1)
  let maxCols = 1
  Object.values(rows).forEach(cols => {
    maxCols = Math.max(maxCols, cols.length)
  })

  const matrix = []
  for (let r = 1; r <= maxRow; r++) {
    const rowCells = []
    const rowBoxes = rows[r] || []
    rowBoxes.sort((a, b) => (a.id - b.id))
    for (let c = 0; c < maxCols; c++) {
      const box = rowBoxes[c] || null
      const riskInfo = box ? boxRiskMap.value[box.id] : null
      rowCells.push({
        key: `${r}-${c}`,
        box,
        riskClass: riskInfo?.riskClass || 'empty',
      })
    }
    matrix.push(rowCells)
  }
  return matrix
})

const floorRiskSummary = computed(() => {
  const summary = [
    { risk: 'danger', label: '高风险', riskClass: 'risk-danger', count: 0 },
    { risk: 'warning', label: '需关注', riskClass: 'risk-warning', count: 0 },
    { risk: 'normal', label: '正常', riskClass: 'risk-normal', count: 0 },
    { risk: 'empty', label: '空闲', riskClass: 'risk-empty', count: 0 },
  ]
  currentFloorBoxes.value.forEach(box => {
    const riskInfo = boxRiskMap.value[box.id]
    if (riskInfo?.riskClass === 'risk-danger') summary[0].count++
    else if (riskInfo?.riskClass === 'risk-warning') summary[1].count++
    else if (riskInfo?.riskClass === 'risk-normal') summary[2].count++
    else summary[3].count++
  })
  return summary.filter(s => s.count > 0)
})

const loadData = async () => {
  try {
    const [list, s, foodList] = await Promise.all([
      getBoxes(),
      getBoxStats(),
      getFoods({ only_active: true }),
    ])
    boxes.value = list
    stats.value = s
    foods.value = foodList
  } catch (e) {}
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

.title-left {
  flex: 1;
}

.view-tabs {
  width: 160px;
  :deep(.van-tab) {
    font-size: 14px;
    font-weight: 500;
    color: #969799;
  }
  :deep(.van-tab--active) {
    color: #323233;
    font-weight: 600;
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
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;

  &:active {
    transform: scale(0.98);
    box-shadow: 0 1px 4px rgba(0,0,0,0.1);
  }

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

    .tag-expiry {
      position: absolute;
      top: 4px;
      right: 4px;
      padding: 1px 6px;
      border-radius: 8px;
      font-size: 10px;
      font-weight: 600;

      &.grace {
        background: #ff976a;
        color: #fff;
      }

      &.released {
        background: #969799;
        color: #fff;
      }

      &.expiring {
        background: #ff976a;
        color: #fff;
        animation: pulse-warning 2s infinite;
      }
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

.heatmap-container {
  padding: 12px 4px;
}

.legend {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;

  .legend-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: #646566;
  }

  .legend-color {
    width: 16px;
    height: 16px;
    border-radius: 4px;
  }
}

.heatmap-matrix {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.matrix-row {
  display: flex;
  align-items: center;
  gap: 8px;

  .row-label {
    width: 28px;
    font-size: 12px;
    color: #969799;
    font-weight: 500;
    text-align: center;
    flex-shrink: 0;
  }

  .row-cells {
    flex: 1;
    display: grid;
    gap: 8px;
  }
}

.matrix-cell {
  aspect-ratio: 1;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  position: relative;
  overflow: hidden;

  &:active {
    transform: scale(0.95);
  }

  &.empty {
    background: #f7f8fa;
    cursor: default;

    &:active {
      transform: none;
    }
  }

  &.risk-empty {
    background: #e8f7ee;
    border: 1px solid #07c160;
  }

  &.risk-normal {
    background: #e8f3ff;
    border: 1px solid #1989fa;
  }

  &.risk-warning {
    background: #fff3e8;
    border: 1px solid #ff976a;
    animation: pulse-warning 2s infinite;
  }

  &.risk-danger {
    background: #fde8e8;
    border: 1px solid #ee0a24;
    animation: pulse-danger 1.5s infinite;
  }

  .cell-count {
    font-size: 22px;
    font-weight: 700;
    line-height: 1.1;
  }

  .cell-name {
    font-size: 10px;
    margin-top: 2px;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    padding: 0 4px;
  }

  .cell-empty {
    font-size: 18px;
    color: #c8c9cc;
  }

  &.risk-empty .cell-count,
  &.risk-empty .cell-name {
    color: #07c160;
  }

  &.risk-normal .cell-count,
  &.risk-normal .cell-name {
    color: #1989fa;
  }

  &.risk-warning .cell-count,
  &.risk-warning .cell-name {
    color: #ff976a;
  }

  &.risk-danger .cell-count,
  &.risk-danger .cell-name {
    color: #ee0a24;
  }
}

@keyframes pulse-warning {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255, 151, 106, 0.4); }
  50% { box-shadow: 0 0 0 6px rgba(255, 151, 106, 0); }
}

@keyframes pulse-danger {
  0%, 100% { box-shadow: 0 0 0 0 rgba(238, 10, 36, 0.5); }
  50% { box-shadow: 0 0 0 8px rgba(238, 10, 36, 0); }
}

.risk-summary {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 16px;
  flex-wrap: wrap;

  .risk-item {
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    border-radius: 16px;
    font-size: 12px;

    &.risk-danger {
      background: #fde8e8;
      color: #ee0a24;
    }

    &.risk-warning {
      background: #fff3e8;
      color: #ff976a;
    }

    &.risk-normal {
      background: #e8f3ff;
      color: #1989fa;
    }

    &.risk-empty {
      background: #e8f7ee;
      color: #07c160;
    }

    .risk-count {
      font-weight: 700;
      font-size: 14px;
    }
  }
}
</style>
