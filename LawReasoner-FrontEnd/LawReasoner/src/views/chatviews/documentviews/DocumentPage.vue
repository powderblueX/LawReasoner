<script setup>
import { ref, reactive } from 'vue';
import { ElMessage, ElButton, ElInput, ElSelect, ElOption, ElForm, ElFormItem, ElTabs, ElTabPane, ElCard, ElTooltip, ElDialog } from 'element-plus';
import { Document, Download, Share, Delete, Edit, Plus, QuestionFilled } from '@element-plus/icons-vue';

// 文书模板类型
const templateTypes = ref([
  { value: 'contract', label: '合同文书' },
  { value: 'litigation', label: '诉讼文书' },
  { value: 'commercial', label: '商业文书' },
  { value: 'estate', label: '房产文书' },
  { value: 'marriage', label: '婚姻家庭文书' }
]);

// 当前选择的模板类型
const selectedType = ref('contract');

// 模板列表
const templates = reactive({
  contract: [
    { id: 1, name: '房屋租赁合同', description: '适用于住宅或商业用房的租赁协议' },
    { id: 2, name: '购销合同', description: '适用于商品买卖交易' },
    { id: 3, name: '劳动合同', description: '用于劳动关系的建立和约定' }
  ],
  litigation: [
    { id: 4, name: '民事起诉状', description: '用于向法院提起民事诉讼' },
    { id: 5, name: '民事答辩状', description: '用于对民事诉讼的答辩' },
    { id: 6, name: '上诉状', description: '用于对一审判决不服提起上诉' }
  ],
  commercial: [
    { id: 7, name: '公司章程', description: '规定公司的组织和活动准则' },
    { id: 8, name: '股权转让协议', description: '用于股权转让交易' }
  ],
  estate: [
    { id: 9, name: '房屋买卖合同', description: '用于房产交易' },
    { id: 10, name: '房屋抵押合同', description: '用于房产抵押贷款' }
  ],
  marriage: [
    { id: 11, name: '离婚协议书', description: '约定离婚事项的法律文书' },
    { id: 12, name: '遗嘱', description: '个人财产分配的法律声明' }
  ]
});

// 我的文书
const myDocuments = ref([
  {
    id: 1,
    name: '与XX公司的劳动合同',
    type: '劳动合同',
    createDate: '2023-09-20',
    lastModified: '2023-09-21'
  },
  {
    id: 2,
    name: '房屋租赁合同（南京路128号）',
    type: '房屋租赁合同',
    createDate: '2023-09-15',
    lastModified: '2023-09-15'
  }
]);

// 当前选择的模板
const selectedTemplate = ref(null);

// 表单数据
const formData = reactive({});
// 表单字段
const formFields = ref([]);

// 文档预览
const documentPreview = ref('');

// 对话框控制
const formDialogVisible = ref(false);
const previewDialogVisible = ref(false);

// 选择模板
const selectTemplate = (template) => {
  selectedTemplate.value = template;
  
  // 根据不同模板设置不同的表单字段
  if (template.id === 1) { // 房屋租赁合同
    formFields.value = [
      { name: 'lessorName', label: '出租方姓名', type: 'text', required: true },
      { name: 'lessorID', label: '出租方身份证号', type: 'text', required: true },
      { name: 'lesseeName', label: '承租方姓名', type: 'text', required: true },
      { name: 'lesseeID', label: '承租方身份证号', type: 'text', required: true },
      { name: 'address', label: '房屋地址', type: 'text', required: true },
      { name: 'area', label: '房屋面积(平方米)', type: 'number', required: true },
      { name: 'startDate', label: '租赁开始日期', type: 'date', required: true },
      { name: 'endDate', label: '租赁结束日期', type: 'date', required: true },
      { name: 'monthlyRent', label: '月租金(元)', type: 'number', required: true },
      { name: 'deposit', label: '押金(元)', type: 'number', required: true }
    ];
  } else if (template.id === 4) { // 民事起诉状
    formFields.value = [
      { name: 'court', label: '受理法院', type: 'text', required: true },
      { name: 'plaintiffName', label: '原告姓名', type: 'text', required: true },
      { name: 'plaintiffGender', label: '原告性别', type: 'select', options: ['男', '女'], required: true },
      { name: 'plaintiffBirth', label: '原告出生日期', type: 'date', required: true },
      { name: 'plaintiffID', label: '原告身份证号', type: 'text', required: true },
      { name: 'plaintiffAddress', label: '原告住所', type: 'text', required: true },
      { name: 'defendantName', label: '被告姓名', type: 'text', required: true },
      { name: 'defendantAddress', label: '被告住所', type: 'text', required: true },
      { name: 'claim', label: '诉讼请求', type: 'textarea', required: true },
      { name: 'facts', label: '事实与理由', type: 'textarea', required: true }
    ];
  } else {
    // 其他模板的表单字段...
    formFields.value = [
      { name: 'field1', label: '字段1', type: 'text', required: true },
      { name: 'field2', label: '字段2', type: 'text', required: true },
      { name: 'field3', label: '字段3', type: 'text', required: true }
    ];
  }
  
  // 初始化表单数据
  formFields.value.forEach(field => {
    formData[field.name] = '';
  });
  
  formDialogVisible.value = true;
};

// 生成文档预览
const generatePreview = () => {
  // 检查必填字段
  const missingFields = formFields.value.filter(field => 
    field.required && !formData[field.name]
  );
  
  if (missingFields.length > 0) {
    ElMessage.warning(`请填写必填字段: ${missingFields.map(f => f.label).join(', ')}`);
    return;
  }
  
  // 根据模板和表单数据生成文档预览
  if (selectedTemplate.value.id === 1) { // 房屋租赁合同
    documentPreview.value = `
房屋租赁合同

出租方（甲方）：${formData.lessorName}
身份证号：${formData.lessorID}

承租方（乙方）：${formData.lesseeName}
身份证号：${formData.lesseeID}

根据《中华人民共和国民法典》及有关法律法规的规定，甲乙双方在平等、自愿的基础上，就房屋租赁的有关事宜达成协议如下：

第一条 房屋基本情况
甲方将坐落于${formData.address}的房屋出租给乙方使用。房屋面积为${formData.area}平方米。

第二条 租赁期限
租赁期限自${formData.startDate}起至${formData.endDate}止，共计_____个月。

第三条 租金及支付方式
月租金为人民币${formData.monthlyRent}元整。乙方应于每月_____日前向甲方支付当月租金。

第四条 押金
乙方应于本合同签订时向甲方支付押金人民币${formData.deposit}元整。合同期满后，如乙方无违约行为，甲方应将押金全额退还给乙方；如乙方有违约行为，甲方有权从押金中扣除相应费用。

...以下省略...
    `;
  } else if (selectedTemplate.value.id === 4) { // 民事起诉状
    documentPreview.value = `
民事起诉状

原告：${formData.plaintiffName}，${formData.plaintiffGender}，${formData.plaintiffBirth}出生，
身份证号码：${formData.plaintiffID}，
住所：${formData.plaintiffAddress}。

被告：${formData.defendantName}，
住所：${formData.defendantAddress}。

诉讼请求：
${formData.claim}

事实与理由：
${formData.facts}

此致
${formData.court}

具状人：${formData.plaintiffName}
日期：${new Date().toISOString().split('T')[0]}
    `;
  } else {
    documentPreview.value = `这是${selectedTemplate.value.name}的预览内容，实际生成时会基于您填写的表单内容生成完整文档。`;
  }
  
  formDialogVisible.value = false;
  previewDialogVisible.value = true;
};

// 保存文档
const saveDocument = () => {
  // 创建新文档对象
  const newDoc = {
    id: myDocuments.value.length + 1,
    name: `新建${selectedTemplate.value.name}`,
    type: selectedTemplate.value.name,
    createDate: new Date().toISOString().split('T')[0],
    lastModified: new Date().toISOString().split('T')[0]
  };
  
  // 添加到文档列表
  myDocuments.value.push(newDoc);
  
  ElMessage.success('文档已保存');
  previewDialogVisible.value = false;
};

// 下载文档
const downloadDocument = () => {
  ElMessage.success('文档已开始下载');
  
  // 模拟下载过程
  setTimeout(() => {
    previewDialogVisible.value = false;
  }, 1000);
};

// 删除文档
const deleteDocument = (id) => {
  const index = myDocuments.value.findIndex(doc => doc.id === id);
  if (index !== -1) {
    myDocuments.value.splice(index, 1);
    ElMessage.success('文档已删除');
  }
};

// 编辑文档
const editDocument = (doc) => {
  ElMessage.info('编辑功能正在开发中');
};

// 分享文档
const shareDocument = (doc) => {
  ElMessage.success('分享链接已复制到剪贴板');
};
</script>

<template>
  <div class="document-container">
    <h1 class="page-title">法律文书生成</h1>
    
    <el-tabs type="border-card" class="document-tabs">
      <el-tab-pane label="文书模板">
        <div class="template-section">
          <div class="template-filter">
            <el-select 
              v-model="selectedType" 
              placeholder="选择文书类型"
              class="type-select"
            >
              <el-option 
                v-for="type in templateTypes" 
                :key="type.value" 
                :label="type.label" 
                :value="type.value"
              ></el-option>
            </el-select>
          </div>
          
          <div class="template-list">
            <el-card 
              v-for="template in templates[selectedType]" 
              :key="template.id"
              class="template-card"
              @click="selectTemplate(template)"
            >
              <div class="template-icon">
                <el-icon :size="40"><Document /></el-icon>
              </div>
              <h3 class="template-name">{{ template.name }}</h3>
              <p class="template-desc">{{ template.description }}</p>
              <el-button type="primary" size="small">使用模板</el-button>
            </el-card>
          </div>
        </div>
      </el-tab-pane>
      
      <el-tab-pane label="我的文书">
        <div class="my-documents">
          <div class="table-header">
            <div class="header-cell name-cell">文档名称</div>
            <div class="header-cell type-cell">文档类型</div>
            <div class="header-cell date-cell">创建日期</div>
            <div class="header-cell date-cell">最后修改</div>
            <div class="header-cell action-cell">操作</div>
          </div>
          
          <div 
            v-for="doc in myDocuments" 
            :key="doc.id"
            class="document-row"
          >
            <div class="document-cell name-cell">
              <el-icon><Document /></el-icon>
              <span>{{ doc.name }}</span>
            </div>
            <div class="document-cell type-cell">{{ doc.type }}</div>
            <div class="document-cell date-cell">{{ doc.createDate }}</div>
            <div class="document-cell date-cell">{{ doc.lastModified }}</div>
            <div class="document-cell action-cell">
              <el-tooltip content="编辑" placement="top">
                <el-button 
                  type="text" 
                  @click="editDocument(doc)"
                  class="action-btn"
                >
                  <el-icon><Edit /></el-icon>
                </el-button>
              </el-tooltip>
              
              <el-tooltip content="下载" placement="top">
                <el-button 
                  type="text" 
                  @click="downloadDocument(doc)"
                  class="action-btn"
                >
                  <el-icon><Download /></el-icon>
                </el-button>
              </el-tooltip>
              
              <el-tooltip content="分享" placement="top">
                <el-button 
                  type="text" 
                  @click="shareDocument(doc)"
                  class="action-btn"
                >
                  <el-icon><Share /></el-icon>
                </el-button>
              </el-tooltip>
              
              <el-tooltip content="删除" placement="top">
                <el-button 
                  type="text" 
                  @click="deleteDocument(doc.id)"
                  class="action-btn delete-btn"
                >
                  <el-icon><Delete /></el-icon>
                </el-button>
              </el-tooltip>
            </div>
          </div>
          
          <div v-if="myDocuments.length === 0" class="no-documents">
            您还没有保存任何文书
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 表单填写对话框 -->
    <el-dialog 
      v-model="formDialogVisible" 
      :title="`填写${selectedTemplate ? selectedTemplate.name : ''}信息`"
      width="60%"
    >
      <el-form v-if="selectedTemplate" label-width="120px">
        <el-form-item 
          v-for="field in formFields"
          :key="field.name"
          :label="field.label"
          :required="field.required"
        >
          <el-input 
            v-if="field.type === 'text'"
            v-model="formData[field.name]"
            placeholder="请输入"
          ></el-input>
          
          <el-input 
            v-else-if="field.type === 'textarea'"
            v-model="formData[field.name]"
            type="textarea"
            rows="4"
            placeholder="请输入"
          ></el-input>
          
          <el-input 
            v-else-if="field.type === 'number'"
            v-model="formData[field.name]"
            type="number"
            placeholder="请输入"
          ></el-input>
          
          <el-select 
            v-else-if="field.type === 'select'"
            v-model="formData[field.name]"
            placeholder="请选择"
            style="width: 100%"
          >
            <el-option 
              v-for="(option, index) in field.options"
              :key="index"
              :label="option"
              :value="option"
            ></el-option>
          </el-select>
          
          <el-input 
            v-else-if="field.type === 'date'"
            v-model="formData[field.name]"
            placeholder="YYYY-MM-DD"
          ></el-input>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="formDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="generatePreview">生成预览</el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 文档预览对话框 -->
    <el-dialog 
      v-model="previewDialogVisible" 
      title="文档预览"
      width="70%"
    >
      <div class="document-preview">
        <pre>{{ documentPreview }}</pre>
      </div>
      
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="previewDialogVisible = false">取消</el-button>
          <el-button type="success" @click="saveDocument">保存文档</el-button>
          <el-button type="primary" @click="downloadDocument">
            <el-icon><Download /></el-icon> 下载文档
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.document-container {
  padding: 20px;
  max-width: 1000px;
  margin: 0 auto;
}

.page-title {
  font-family: 'KaiTi', serif;
  text-align: center;
  margin-bottom: 20px;
  color: #333;
}

.document-tabs {
  min-height: 600px;
}

.template-section {
  padding: 20px;
}

.template-filter {
  margin-bottom: 20px;
}

.type-select {
  width: 200px;
}

.template-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.template-card {
  width: calc(33.333% - 20px);
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s;
}

.template-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.template-icon {
  margin-bottom: 15px;
}

.template-name {
  font-size: 18px;
  margin-bottom: 10px;
  color: #333;
  text-align: center;
}

.template-desc {
  color: #666;
  text-align: center;
  margin-bottom: 15px;
  height: 40px;
  overflow: hidden;
}

.my-documents {
  padding: 10px;
}

.table-header {
  display: flex;
  background-color: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  font-weight: 600;
  color: #333;
  margin-bottom: 10px;
}

.header-cell {
  padding: 0 10px;
}

.document-row {
  display: flex;
  padding: 15px 10px;
  border-bottom: 1px solid #eee;
  align-items: center;
}

.document-cell {
  padding: 0 10px;
}

.name-cell {
  flex: 3;
  display: flex;
  align-items: center;
  gap: 10px;
}

.type-cell {
  flex: 1;
}

.date-cell {
  flex: 1;
}

.action-cell {
  flex: 2;
  display: flex;
  justify-content: flex-end;
  gap: 5px;
}

.action-btn {
  font-size: 18px;
}

.delete-btn:hover {
  color: #F56C6C;
}

.no-documents {
  text-align: center;
  padding: 30px;
  color: #909399;
}

.document-preview {
  max-height: 60vh;
  overflow-y: auto;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: #f8f9fa;
}

pre {
  white-space: pre-wrap;
  font-family: 'SimSun', serif;
  font-size: 14px;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .template-card {
    width: 100%;
  }
  
  .template-filter {
    display: flex;
    justify-content: center;
  }
  
  .document-row {
    flex-wrap: wrap;
  }
  
  .document-cell {
    padding: 5px 10px;
  }
  
  .name-cell {
    flex: 1 0 100%;
    margin-bottom: 10px;
  }
  
  .type-cell, .date-cell {
    flex: 1 0 33%;
  }
  
  .action-cell {
    flex: 1 0 100%;
    justify-content: flex-start;
    margin-top: 10px;
  }
}
</style> 