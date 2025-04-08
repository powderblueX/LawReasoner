<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage, ElTree, ElInput, ElButton, ElTabs, ElTabPane, ElCard } from 'element-plus';
import { Search, Document, ArrowRight } from '@element-plus/icons-vue';
import BackToHome from '@/components/BackToHome.vue';
import minfadianData from '@/assets/files/minfadian.json';

// 获取法条内容的函数
const getLawContent = (articleNumber) => {
  // 直接通过索引获取法条内容
  const index = articleNumber - 1; // 因为数组索引从0开始，所以需要减1
  if (index >= 0 && index < minfadianData.length) {
    return minfadianData[index].output;
  }
  return `第${articleNumber}条 暂无内容`;
};

// 获取指定范围内的法条内容
const getLawContents = (startArticle, endArticle) => {
  const contents = [];
  for (let i = startArticle; i <= endArticle; i++) {
    const content = getLawContent(i);
    contents.push({
      label: `第${i}条`,
      content: content
    });
  }
  return contents;
};

// 知识库章节数据
const chapters = reactive([
  {
    label: '第一编 总则',
    children: [
      { 
        label: '第一章 基本规定',
        startArticle: 1,
        endArticle: 12
      },
      {
        label: '第二章 自然人',
        children: [
          {
            label: '第一节 民事权利能力和民事行为能力',
            startArticle: 13,
            endArticle: 25
          },
          {
            label: '第二节 监护',
            startArticle: 26,
            endArticle: 39
          },
          {
            label: '第三节 宣告失踪和宣告死亡',
            startArticle: 40,
            endArticle: 53
          },
          {
            label: '第四节 个体工商户和农村承包经营户',
            startArticle: 54,
            endArticle: 56
          }
        ]
      },
      {
        label: '第三章 法人',
        children: [
          { 
            label: '第一节 一般规定',
            startArticle: 57,
            endArticle: 75
          },
          { 
            label: '第二节 营利法人',
            startArticle: 76,
            endArticle: 86
          },
          { 
            label: '第三节 非营利法人',
            startArticle: 87,
            endArticle: 95
          },
          { 
            label: '第四节 特别法人',
            startArticle: 96,
            endArticle: 101
          }
        ]
      },
      { 
        label: '第四章 非法人组织',
        startArticle: 102,
        endArticle: 108
      },
      { 
        label: '第五章 民事权利',
        startArticle: 109,
        endArticle: 132
      },
      {
        label: '第六章 民事法律行为',
        children: [
          { 
            label: '第一节 一般规定',
            startArticle: 133,
            endArticle: 136
          },
          { 
            label: '第二节 意思表示',
            startArticle: 137,
            endArticle: 142
          },
          { 
            label: '第三节 民事法律行为的效力',
            startArticle: 143,
            endArticle: 157
          },
          { 
            label: '第四节 民事法律行为的附条件和附期限',
            startArticle: 158,
            endArticle: 160
          }
        ]
      },
      {
        label: '第七章 代理',
        children: [
          { 
            label: '第一节 一般规定',
            startArticle: 161,
            endArticle: 164
          },
          { 
            label: '第二节 委托代理',
            startArticle: 165,
            endArticle: 172
          },
          { 
            label: '第三节 代理终止',
            startArticle: 173,
            endArticle: 175
          }
        ]
      },
      { 
        label: '第八章 民事责任',
        startArticle: 176,
        endArticle: 187
      },
      { 
        label: '第九章 诉讼时效',
        startArticle: 188,
        endArticle: 199
      },
      { 
        label: '第十章 期间计算',
        startArticle: 200,
        endArticle: 204
      }
    ]
  },
  {
    label: '第二编 物权',
    children: [
      {
        label: '第一分编 通则',
        children: [
          { 
            label: '第一章 一般规定',
            startArticle: 205,
            endArticle: 207
          },
          {
            label: '第二章 物权的设立、变更、转让和消灭',
            children: [
              { 
                label: '第一节 不动产登记',
                startArticle: 208,
                endArticle: 223
              },
              { 
                label: '第二节 动产交付',
                startArticle: 224,
                endArticle: 228
              },
              { 
                label: '第三节 其他规定',
                startArticle: 229,
                endArticle: 232
              }
            ]
          },
          { 
            label: '第三章 物权的保护',
            startArticle: 233,
            endArticle: 239
          }
        ]
      },
      {
        label: '第二分编 所有权',
        children: [
          { 
            label: '第四章 一般规定',
            startArticle: 240,
            endArticle: 245
          },
          { 
            label: '第五章 国家所有权和集体所有权、私人所有权',
            startArticle: 246,
            endArticle: 270
          },
          { 
            label: '第六章 业主的建筑物区分所有权',
            startArticle: 271,
            endArticle: 287
          },
          { 
            label: '第七章 相邻关系',
            startArticle: 288,
            endArticle: 296
          },
          { 
            label: '第八章 共有',
            startArticle: 297,
            endArticle: 310
          },
          { 
            label: '第九章 所有权取得的特别规定',
            startArticle: 311,
            endArticle: 322
          }
        ]
      },
      {
        label: '第三分编 用益物权',
        children: [
          { 
            label: '第十章 一般规定',
            startArticle: 323,
            endArticle: 329
          },
          { 
            label: '第十一章 土地承包经营权',
            startArticle: 330,
            endArticle: 343
          },
          { 
            label: '第十二章 建设用地使用权',
            startArticle: 344,
            endArticle: 361
          },
          { 
            label: '第十三章 宅基地使用权',
            startArticle: 362,
            endArticle: 365
          },
          { 
            label: '第十四章 居住权',
            startArticle: 366,
            endArticle: 371
          },
          { 
            label: '第十五章 地役权',
            startArticle: 372,
            endArticle: 385
          }
        ]
      },
      {
        label: '第四分编 担保物权',
        children: [
          { 
            label: '第十六章 一般规定',
            startArticle: 386,
            endArticle: 393
          },
          {
            label: '第十七章 抵押权',
            children: [
              { 
                label: '第一节 一般抵押权',
                startArticle: 394,
                endArticle: 419
              },
              { 
                label: '第二节 最高额抵押权',
                startArticle: 420,
                endArticle: 424
              }
            ]
          },
          {
            label: '第十八章 质权',
            children: [
              { 
                label: '第一节 动产质权',
                startArticle: 425,
                endArticle: 439
              },
              { 
                label: '第二节 权利质权',
                startArticle: 440,
                endArticle: 446
              }
            ]
          },
          { 
            label: '第十九章 留置权',
            startArticle: 447,
            endArticle: 457
          }
        ]
      },
      {
        label: '第五分编 占有',
        children: [
          { 
            label: '第二十章 占有',
            startArticle: 458,
            endArticle: 462
          }
        ]
      }
    ]
  },
  {
    label: '第三编 合同',
    children: [
      {
        label: '第一分编 通则',
        children: [
          { 
            label: '第一章 一般规定',
            startArticle: 463,
            endArticle: 470
          },
          { 
            label: '第二章 合同的订立',
            startArticle: 471,
            endArticle: 501
          },
          { 
            label: '第三章 合同的效力',
            startArticle: 502,
            endArticle: 508
          },
          { 
            label: '第四章 合同的履行',
            startArticle: 509,
            endArticle: 534
          },
          { 
            label: '第五章 合同的保全',
            startArticle: 535,
            endArticle: 542
          },
          { 
            label: '第六章 合同的变更和转让',
            startArticle: 543,
            endArticle: 556
          },
          { 
            label: '第七章 合同的权利义务终止',
            startArticle: 557,
            endArticle: 576
          },
          { 
            label: '第八章 违约责任',
            startArticle: 577,
            endArticle: 594
          }
        ]
      },
      {
        label: '第二分编 典型合同',
        children: [
          { 
            label: '第九章 买卖合同',
            startArticle: 595,
            endArticle: 647
          },
          { 
            label: '第十章 供用电、水、气、热力合同',
            startArticle: 648,
            endArticle: 656
          },
          { 
            label: '第十一章 赠与合同',
            startArticle: 657,
            endArticle: 666
          },
          { 
            label: '第十二章 借款合同',
            startArticle: 667,
            endArticle: 680
          },
          {
            label: '第十三章 保证合同',
            children: [
              { 
                label: '第一节 一般规定',
                startArticle: 681,
                endArticle: 690
              },
              { 
                label: '第二节 保证责任',
                startArticle: 691,
                endArticle: 702
              }
            ]
          },
          { 
            label: '第十四章 租赁合同',
            startArticle: 703,
            endArticle: 734
          },
          { 
            label: '第十五章 融资租赁合同',
            startArticle: 735,
            endArticle: 760
          },
          { 
            label: '第十六章 保理合同',
            startArticle: 761,
            endArticle: 769
          },
          { 
            label: '第十七章 承揽合同',
            startArticle: 770,
            endArticle: 787
          },
          { 
            label: '第十八章 建设工程合同',
            startArticle: 788,
            endArticle: 808
          },
          {
            label: '第十九章 运输合同',
            children: [
              { 
                label: '第一节 一般规定',
                startArticle: 809,
                endArticle: 813
              },
              { 
                label: '第二节 客运合同',
                startArticle: 814,
                endArticle: 824
              },
              { 
                label: '第三节 货运合同',
                startArticle: 825,
                endArticle: 837
              },
              { 
                label: '第四节 多式联运合同',
                startArticle: 838,
                endArticle: 842
              }
            ]
          },
          {
            label: '第二十章 技术合同',
            children: [
              { 
                label: '第一节 一般规定',
                startArticle: 843,
                endArticle: 850
              },
              { 
                label: '第二节 技术开发合同',
                startArticle: 851,
                endArticle: 861
              },
              { 
                label: '第三节 技术转让合同和技术许可合同',
                startArticle: 862,
                endArticle: 877
              },
              { 
                label: '第四节 技术咨询合同和技术服务合同',
                startArticle: 878,
                endArticle: 887
              }
            ]
          },
          { 
            label: '第二十一章 保管合同',
            startArticle: 888,
            endArticle: 903
          },
          { 
            label: '第二十二章 仓储合同',
            startArticle: 904,
            endArticle: 918
          },
          { 
            label: '第二十三章 委托合同',
            startArticle: 919,
            endArticle: 936
          },
          { 
            label: '第二十四章 物业服务合同',
            startArticle: 937,
            endArticle: 950
          },
          { 
            label: '第二十五章 行纪合同',
            startArticle: 951,
            endArticle: 960
          },
          { 
            label: '第二十六章 中介合同',
            startArticle: 961,
            endArticle: 966
          },
          { 
            label: '第二十七章 合伙合同',
            startArticle: 967,
            endArticle: 978
          }
        ]
      },
      {
        label: '第三分编 准合同',
        children: [
          { 
            label: '第二十八章 无因管理',
            startArticle: 979,
            endArticle: 984
          },
          { 
            label: '第二十九章 不当得利',
            startArticle: 985,
            endArticle: 988
          }
        ]
      }
    ]
  },
  {
    label: '第四编 人格权',
    children: [
      { 
        label: '第一章 一般规定',
        startArticle: 989,
        endArticle: 1001
      },
      { 
        label: '第二章 生命权、身体权和健康权',
        startArticle: 1002,
        endArticle: 1011
      },
      { 
        label: '第三章 姓名权和名称权',
        startArticle: 1012,
        endArticle: 1017
      },
      { 
        label: '第四章 肖像权',
        startArticle: 1018,
        endArticle: 1023
      },
      { 
        label: '第五章 名誉权和荣誉权',
        startArticle: 1024,
        endArticle: 1031
      },
      { 
        label: '第六章 隐私权和个人信息保护',
        startArticle: 1032,
        endArticle: 1039
      }
    ]
  },
  {
    label: '第五编 婚姻家庭',
    children: [
      { 
        label: '第一章 一般规定',
        startArticle: 1040,
        endArticle: 1045
      },
      { 
        label: '第二章 结婚',
        startArticle: 1046,
        endArticle: 1054
      },
      {
        label: '第三章 家庭关系',
        children: [
          { 
            label: '第一节 夫妻关系',
            startArticle: 1055,
            endArticle: 1066
          },
          { 
            label: '第二节 父母子女关系和其他近亲属关系',
            startArticle: 1067,
            endArticle: 1075
          }
        ]
      },
      { 
        label: '第四章 离婚',
        startArticle: 1076,
        endArticle: 1092
      },
      {
        label: '第五章 收养',
        children: [
          { 
            label: '第一节 收养关系的成立',
            startArticle: 1093,
            endArticle: 1110
          },
          { 
            label: '第二节 收养的效力',
            startArticle: 1111,
            endArticle: 1113
          },
          { 
            label: '第三节 收养关系的解除',
            startArticle: 1114,
            endArticle: 1118
          }
        ]
      }
    ]
  },
  {
    label: '第六编 继承',
    children: [
      { 
        label: '第一章 一般规定',
        startArticle: 1119,
        endArticle: 1125
      },
      { 
        label: '第二章 法定继承',
        startArticle: 1126,
        endArticle: 1132
      },
      { 
        label: '第三章 遗嘱继承和遗赠',
        startArticle: 1133,
        endArticle: 1146
      },
      { 
        label: '第四章 遗产的处理',
        startArticle: 1147,
        endArticle: 1163
      }
    ]
  },
  {
    label: '第七编 侵权责任',
    children: [
      { 
        label: '第一章 一般规定',
        startArticle: 1164,
        endArticle: 1178
      },
      { 
        label: '第二章 损害赔偿',
        startArticle: 1179,
        endArticle: 1187
      },
      { 
        label: '第三章 责任主体的特殊规定',
        startArticle: 1188,
        endArticle: 1201
      },
      { 
        label: '第四章 产品责任',
        startArticle: 1202,
        endArticle: 1207
      },
      { 
        label: '第五章 机动车交通事故责任',
        startArticle: 1208,
        endArticle: 1217
      },
      { 
        label: '第六章 医疗损害责任',
        startArticle: 1218,
        endArticle: 1228
      },
      { 
        label: '第七章 环境污染和生态破坏责任',
        startArticle: 1229,
        endArticle: 1235
      },
      { 
        label: '第八章 高度危险责任',
        startArticle: 1236,
        endArticle: 1244
      },
      { 
        label: '第九章 饲养动物损害责任',
        startArticle: 1245,
        endArticle: 1251
      },
      { 
        label: '第十章 建筑物和物件损害责任',
        startArticle: 1252,
        endArticle: 1258
      }
    ]
  },
  {
    label: '附则',
    startArticle: 1259,
    endArticle: 1260
  }
]);

// 搜索相关
const searchKeyword = ref('');
const searchResults = ref([]);
const hasSearched = ref(false);  // 添加标记表示是否已执行搜索

// 选中的章节内容
const selectedContents = ref([]);
const selectedTitle = ref('');

// 搜索条款
const searchLaw = () => {
  if (!searchKeyword.value) {
    ElMessage.warning('请输入搜索关键词');
    return;
  }
  
  // 直接从minfadian.json中搜索相关内容
  searchResults.value = minfadianData
    .map((item, index) => ({
      title: `第${index + 1}条`,
      content: item.output
    }))
    .filter(item => item.content.toLowerCase().includes(searchKeyword.value.toLowerCase()));
  
  hasSearched.value = true;  // 标记已执行搜索
};

// 选择条款
const selectLaw = (title, content) => {
  selectedTitle.value = title;
  selectedContents.value = [{ label: title, content: content }];
};

// 节点点击事件
const handleNodeClick = (data) => {
  if (data.startArticle && data.endArticle) {
    selectedTitle.value = data.label;
    selectedContents.value = getLawContents(data.startArticle, data.endArticle);
  }
};

// 默认选中第一章
onMounted(() => {
  if (chapters[0].children && chapters[0].children[0]) {
    const firstChapter = chapters[0].children[0];
    selectedTitle.value = firstChapter.label;
    selectedContents.value = getLawContents(firstChapter.startArticle, firstChapter.endArticle);
  }
});
</script>

<template>
  <div class="knowledge-container">
    <h1 class="page-title">民法典知识库</h1>
    <div class="law-info">
      <p>《中华人民共和国民法典》已由中华人民共和国第十三届全国人民代表大会第三次会议于 2020 年 5 月 28 日通过，自 2021 年 1 月 1 日起施行。</p>
      <p>
        <span>制定机关：全国人民代表大会</span>
        <span class="info-divider">|</span>
        <span>生效日期：2021 年 1 月 1 日</span>
      </p>
    </div>
    
    <el-tabs type="border-card" class="knowledge-tabs">
      <el-tab-pane label="章节浏览">
        <div class="knowledge-content">
          <div class="knowledge-tree">
            <el-tree 
              :data="chapters" 
              :props="{ children: 'children', label: 'label' }"
              @node-click="handleNodeClick"
              default-expand-all
            />
          </div>
          <div class="knowledge-detail">
            <el-card class="law-content">
              <h2>{{ selectedTitle }}</h2>
              <div v-for="(item, index) in selectedContents" :key="index" class="law-item">
                <h3>{{ item.label }}</h3>
                <p>{{ item.content }}</p>
              </div>
            </el-card>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="关键词搜索">
        <div class="search-section">
          <el-input 
            v-model="searchKeyword" 
            placeholder="输入关键词搜索相关法律条款" 
            class="search-input"
          >
            <template #append>
              <el-button :icon="Search" @click="searchLaw">搜索</el-button>
            </template>
          </el-input>
          
          <div class="search-container">
          <div class="search-results">
              <h3>搜索结果</h3>
            <div 
              v-for="(result, index) in searchResults" 
              :key="index"
              class="search-result-item"
              @click="selectLaw(result.title, result.content)"
            >
                <h4>{{ result.title }}</h4>
              <p>{{ result.content.substring(0, 100) + '...' }}</p>
              </div>
              
              <div v-if="searchResults.length === 0 && hasSearched" class="no-results">
                没有找到相关条款
              </div>
              
              <div v-if="!hasSearched" class="no-results">
                请输入关键词并点击搜索按钮
              </div>
            </div>
            
            <div class="selected-content">
              <h3>选中条款详情</h3>
              <el-card v-if="selectedContents.length > 0" class="law-content">
                <h2>{{ selectedTitle }}</h2>
                <div v-for="(item, index) in selectedContents" :key="index" class="law-item">
                  <h3>{{ item.label }}</h3>
                  <p>{{ item.content }}</p>
                </div>
              </el-card>
              <div v-else class="no-selection">
                请从搜索结果中选择一条条款查看详情
              </div>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <BackToHome />
  </div>
</template>

<style scoped>
.knowledge-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-family: 'KaiTi', serif;
  text-align: center;
  margin-bottom: 10px;
  color: #333;
}

.law-info {
  text-align: center;
  margin-bottom: 20px;
  color: #666;
  font-size: 14px;
  line-height: 1.8;
}

.info-divider {
  margin: 0 10px;
  color: #ddd;
}

.knowledge-tabs {
  min-height: 600px;
}

.knowledge-content {
  display: flex;
  height: 70vb;
}

.knowledge-tree {
  width: 300px;
  overflow-y: auto;
  border-right: 1px solid #eee;
  padding-right: 15px;
}

.knowledge-detail {
  flex: 1;
  padding-left: 20px;
  overflow-y: auto;
}

.search-section {
  padding: 20px;
}

.search-input {
  margin-bottom: 20px;
}

.search-container {
  display: flex;
  gap: 20px;
  height: 600px;
}

.search-results {
  flex: 1;
  overflow-y: auto;
  border-right: 1px solid #eee;
  padding-right: 15px;
}

.selected-content {
  flex: 1;
  overflow-y: auto;
}

.search-results h3,
.selected-content h3 {
  margin-bottom: 15px;
  color: #333;
  font-size: 18px;
}

.search-result-item {
  padding: 15px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  transition: background-color 0.3s;
}

.search-result-item:hover {
  background-color: #f5f7fa;
}

.search-result-item h4 {
  color: #409EFF;
  margin-bottom: 8px;
}

.search-result-item p {
  color: #666;
  line-height: 1.5;
}

.no-selection {
  text-align: center;
  padding: 40px;
  color: #909399;
  font-size: 16px;
}

.no-results {
  text-align: center;
  padding: 40px;
  color: #909399;
  font-size: 16px;
}

.law-content {
  margin-top: 20px;
  font-family: 'KaiTi', serif;
}

.law-item {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.law-item:last-child {
  border-bottom: none;
}

.law-item h3 {
  color: #409EFF;
  margin-bottom: 10px;
}

.law-item p {
  line-height: 1.6;
  color: #333;
}
</style> 