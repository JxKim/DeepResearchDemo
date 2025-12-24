import React, { useState, useEffect } from 'react';
import { 
  Card, Table, Button, Typography, message, Modal, Input, List, Tag, Empty, 
  Layout, Menu, Form, Space, Upload, Select, Radio, Badge, Tooltip, Steps,
  Cascader, InputNumber
} from 'antd';
import { 
  SyncOutlined, ExperimentOutlined, SearchOutlined, PlusOutlined, 
  FolderOutlined, UploadOutlined, FileTextOutlined, DeleteOutlined,
  CheckCircleOutlined, CloseCircleOutlined, ClockCircleOutlined, LoadingOutlined,
  FilePdfOutlined, FileWordOutlined, FileUnknownOutlined
} from '@ant-design/icons';
import api from '../api';

const { Title, Text, Paragraph } = Typography;
const { Search } = Input;
const { Sider, Content } = Layout;
const { Option } = Select;

// --- 枚举定义 ---
const ParseStatus = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed'
};

const RetrievalStrategy = {
  HYBRID: 'hybrid',
  FULL_TEXT: 'full_text',
  VECTOR: 'vector'
};

const KnowledgeApi = {
  getCategories: async () => {
    const response = await api.get('/knowledge/categories');
    const data = response.data.data || [];
    return data.map((c) => ({ ...c, id: String(c.id) }));
  },
  createCategory: async (name, description) => {
    const response = await api.post('/knowledge/category', { name, description });
    return { ...response.data, id: String(response.data.id) };
  },
  deleteCategory: async (categoryId) => {
    await api.delete(`/knowledge/category/${categoryId}`);
    return true;
  },
  getFiles: async (categoryId) => {
    const response = await api.get(`/knowledge/category/${categoryId}/files`);
    return response.data.data || [];
  },
  uploadFile: async (categoryId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category_id', categoryId);
    const response = await api.post('/knowledge/upload', formData);
    return response.data.data;
  },
  startParse: async (categoryId, fileId) => {
    const response = await api.post('/knowledge/parse/submit', null, {
      params: { file_id: fileId, category_id: categoryId }
    });
    return response.data.data;
  },
  checkParseStatus: async (fileId) => {
    const response = await api.get(`/knowledge/parse/progress/${fileId}`);
    return response.data.data;
  },
  testRecall: async (query, strategy, fileId, limit = 3) => {
    const response = await api.post('/knowledge/recall/test', {
      query,
      limit,
      search_strategy: strategy,
      file_id: fileId
    });
    return response.data.data || [];
  },
  deleteFile: async (categoryId, fileId) => {
    await api.delete(`/knowledge/${fileId}`, { params: { category_id: categoryId } });
    return true;
  }
};

const KnowledgeBase = () => {
  // --- 状态管理 ---
  const [categories, setCategories] = useState([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState(null);
  const [files, setFiles] = useState([]);
  const [loadingFiles, setLoadingFiles] = useState(false);
  
  // 新建分类相关
  const [isCategoryModalVisible, setIsCategoryModalVisible] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [newCategoryDesc, setNewCategoryDesc] = useState('');
  const [creatingCategory, setCreatingCategory] = useState(false);

  // 上传相关
  const [uploading, setUploading] = useState(false);

  // 召回测试相关
  const [isTestModalVisible, setIsTestModalVisible] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  
  // Step 1: 选择文档
  const [fileOptions, setFileOptions] = useState([]);
  const [selectedTestDoc, setSelectedTestDoc] = useState([]); // [categoryId, fileId]

  // Step 2: 策略配置
  const [testStrategy, setTestStrategy] = useState(RetrievalStrategy.HYBRID);
  const [testLimit, setTestLimit] = useState(3);

  // Step 3: 测试结果
  const [testQuery, setTestQuery] = useState('');
  const [testResults, setTestResults] = useState([]);
  const [isTesting, setIsTesting] = useState(false);

  // --- 初始化加载 ---
  useEffect(() => {
    loadCategories();
  }, []);

  useEffect(() => {
    if (selectedCategoryId) {
      loadFiles(selectedCategoryId);
    } else {
      setFiles([]);
    }
  }, [selectedCategoryId]);

  // 加载级联选择器数据
  useEffect(() => {
    if (isTestModalVisible) {
      loadFileOptions();
      setCurrentStep(0);
      setTestResults([]);
      setTestQuery('');
    }
  }, [isTestModalVisible]);

  // --- 业务逻辑方法 ---

  const loadCategories = async () => {
    try {
      const data = await KnowledgeApi.getCategories();
      setCategories(data);
      if (data.length > 0 && !selectedCategoryId) {
        setSelectedCategoryId(String(data[0].id));
      }
    } catch {
      message.error('加载分类失败');
    }
  };

  const loadFiles = async (categoryId) => {
    setLoadingFiles(true);
    try {
      const data = await KnowledgeApi.getFiles(categoryId);
      setFiles(data);
    } catch {
      message.error('加载文件失败');
    } finally {
      setLoadingFiles(false);
    }
  };

  const loadFileOptions = async () => {
    try {
      const categoryList = await KnowledgeApi.getCategories();
      const fileLists = await Promise.all(
        (categoryList || []).map(async (c) => {
          const fs = await KnowledgeApi.getFiles(c.id);
          return { category: c, files: fs || [] };
        })
      );
      const options = fileLists.map(({ category, files: fs }) => ({
        value: category.id,
        label: category.name,
        children: fs.map((f) => {
          const isParsed = f?.parse_status === ParseStatus.COMPLETED;
          return {
            value: f.file_id,
            label: isParsed ? f.file_name : `${f.file_name} (未解析)`,
            disabled: !isParsed,
          };
        })
      }));
      setFileOptions(options);
    } catch {
      setFileOptions([]);
    }
  };

  const handleCreateCategory = async () => {
    if (!newCategoryName.trim()) {
      message.warning('请输入分类名称');
      return;
    }
    setCreatingCategory(true);
    try {
      const newCategory = await KnowledgeApi.createCategory(newCategoryName, newCategoryDesc);
      setCategories([...categories, newCategory]);
      message.success('分类创建成功');
      setIsCategoryModalVisible(false);
      setNewCategoryName('');
      setNewCategoryDesc('');
      // 自动选中新分类
      setSelectedCategoryId(String(newCategory.id));
    } catch {
      message.error('创建失败');
    } finally {
      setCreatingCategory(false);
    }
  };

  const handleDeleteCategory = () => {
    if (!selectedCategoryId) return;
    
    const category = categories.find(c => String(c.id) === String(selectedCategoryId));
    
    Modal.confirm({
      title: '确认删除知识库分类?',
      icon: <DeleteOutlined style={{ color: 'red' }} />,
      content: (
        <div>
          <p>您正在删除分类：<Text strong>{category?.name}</Text></p>
          <p style={{ color: '#ff4d4f' }}>注意：此操作不可恢复，该分类下的所有文件也将被一并删除。</p>
        </div>
      ),
      okText: '确认删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await KnowledgeApi.deleteCategory(selectedCategoryId);
          const newCategories = categories.filter(c => String(c.id) !== String(selectedCategoryId));
          setCategories(newCategories);
          
          if (newCategories.length > 0) {
            setSelectedCategoryId(String(newCategories[0].id));
          } else {
            setSelectedCategoryId(null);
          }
          setFiles([]);
          message.success('分类已删除');
        } catch {
          message.error('删除失败');
        }
      },
    });
  };

  // 模拟文件上传
  const handleUpload = async (file) => {
    if (!selectedCategoryId) {
      message.warning('请先选择一个分类');
      return false;
    }

    setUploading(true);
    try {
      // 1. 上传文件
      const newFile = await KnowledgeApi.uploadFile(selectedCategoryId, file);
      const updatedFiles = [newFile, ...files];
      setFiles(updatedFiles);
      message.success('文件上传成功');
      setCategories(prev => prev.map(c => String(c.id) === String(selectedCategoryId) ? { ...c, count: (c.count || 0) + 1 } : c));

      // 2. 询问是否解析
      Modal.confirm({
        title: '是否立即解析?',
        content: `文件 "${newFile.file_name}" 已上传，是否立即开始解析？`,
        okText: '立即解析',
        cancelText: '稍后',
        onOk: () => handleParse(newFile.file_id),
      });

    } catch {
      message.error('上传失败');
    } finally {
      setUploading(false);
    }
    return false; // 阻止 Antd Upload 默认上传行为
  };

  // 解析流程
  const handleParse = async (fileId) => {
    updateFileStatus(fileId, { parse_status: ParseStatus.PROCESSING });
    try {
      await KnowledgeApi.startParse(selectedCategoryId, fileId);
      const poll = async () => {
        try {
          const result = await KnowledgeApi.checkParseStatus(fileId);
          if (!result) {
            updateFileStatus(fileId, { parse_status: ParseStatus.FAILED });
            return;
          }
          updateFileStatus(fileId, {
            parse_status: result.status,
            chunk_num: result.chunk_num ?? undefined,
            updated_at: result.updated_at ?? undefined
          });
          if (result.status === ParseStatus.COMPLETED) {
            message.success('解析完成');
            await loadFiles(selectedCategoryId);
            return;
          }
          if (result.status === ParseStatus.FAILED) {
            message.error('解析失败');
            return;
          }
          setTimeout(poll, 2000);
        } catch {
          updateFileStatus(fileId, { parse_status: ParseStatus.FAILED });
        }
      };
      setTimeout(poll, 1500);
    } catch {
      message.error('启动解析失败');
      updateFileStatus(fileId, { parse_status: ParseStatus.FAILED });
    }
  };

  const updateFileStatus = (fileId, updates) => {
    setFiles(prevFiles => prevFiles.map(f => 
      f.file_id === fileId ? { ...f, ...updates } : f
    ));
  };

  const handleDeleteFile = (fileId) => {
    if (!selectedCategoryId) return;
    const file = files.find(f => f.file_id === fileId);
    Modal.confirm({
      title: '确认删除文件?',
      icon: <DeleteOutlined style={{ color: 'red' }} />,
      content: (
        <div>
          <p>您正在删除文件：<Text strong>{file?.file_name}</Text></p>
          <p style={{ color: '#ff4d4f' }}>注意：此操作不可恢复。</p>
        </div>
      ),
      okText: '确认删除',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        try {
          await KnowledgeApi.deleteFile(selectedCategoryId, fileId);
          setFiles(prev => prev.filter(f => f.file_id !== fileId));
          setCategories(prev => prev.map(c => String(c.id) === String(selectedCategoryId) ? { ...c, count: Math.max((c.count || 0) - 1, 0) } : c));
          message.success('文件已删除');
        } catch {
          message.error('删除失败');
        }
      }
    });
  };

  const handleTestSearch = async (searchValue) => {
    const query = (typeof searchValue === 'string' ? searchValue : testQuery).trim();
    if (!query) return;
    if (selectedTestDoc.length < 2) {
      message.warning('请先选择测试文档');
      return;
    }

    const selectedCategoryOption = fileOptions.find((c) => c.value === selectedTestDoc[0]);
    const selectedFileOption = selectedCategoryOption?.children?.find((f) => f.value === selectedTestDoc[1]);
    if (selectedFileOption?.disabled) {
      message.warning('该文件尚未解析，无法测试召回');
      return;
    }
    
    setIsTesting(true);
    setTestQuery(query);
    try {
      const fileId = selectedTestDoc[1]; // 选中的是第二级(文件ID)
      const results = await KnowledgeApi.testRecall(query, testStrategy, fileId, testLimit);
      setTestResults(results);
      if (results.length === 0) {
        message.info('未找到相关内容');
      }
    } catch {
      message.error('测试请求失败');
    } finally {
      setIsTesting(false);
    }
  };

  // --- 渲染辅助函数 ---

  const getStatusTag = (status) => {
    switch (status) {
      case ParseStatus.PENDING:
        return <Tag icon={<ClockCircleOutlined />} color="default">等待解析</Tag>;
      case ParseStatus.PROCESSING:
        return <Tag icon={<SyncOutlined spin />} color="processing">解析中</Tag>;
      case ParseStatus.COMPLETED:
        return <Tag icon={<CheckCircleOutlined />} color="success">解析成功</Tag>;
      case ParseStatus.FAILED:
        return <Tag icon={<CloseCircleOutlined />} color="error">解析失败</Tag>;
      default:
        return <Tag>未知状态</Tag>;
    }
  };

  const columns = [
    {
      title: '文件名',
      dataIndex: 'file_name',
      key: 'file_name',
      render: (text) => <Space><FileTextOutlined />{text}</Space>
    },
    {
      title: '上传时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (timestamp) => timestamp ? new Date(timestamp).toLocaleString() : '-'
    },
    {
      title: '解析状态',
      dataIndex: 'parse_status',
      key: 'parse_status',
      render: (status) => getStatusTag(status)
    },
    {
      title: 'Chunk数量',
      dataIndex: 'chunk_num',
      key: 'chunk_num',
      align: 'center',
    },
    {
      title: '操作',
      key: 'action',
      render: (_, record) => (
        <Space>
          <Button 
            type="link" 
            size="small"
            disabled={record.parse_status === ParseStatus.PROCESSING}
            onClick={() => handleParse(record.file_id)}
          >
            {record.parse_status === ParseStatus.COMPLETED ? '重新解析' : '解析'}
          </Button>
          <Button type="link" danger size="small" onClick={() => handleDeleteFile(record.file_id)}>删除</Button>
        </Space>
      )
    }
  ];

  // 渲染召回测试步骤内容
  const renderStepContent = () => {
    switch (currentStep) {
      case 0: // 选择文档
        return (
          <div style={{ padding: '24px 0', minHeight: '200px' }}>
            <Form layout="vertical">
              <Form.Item label="选择测试文档 (从已上传文档中选择)" required>
                <Cascader
                  options={fileOptions}
                  placeholder="请选择: 分类 / 文件"
                  value={selectedTestDoc}
                  onChange={setSelectedTestDoc}
                  style={{ width: '100%' }}
                  size="large"
                  expandTrigger="hover"
                />
              </Form.Item>
              <div style={{ marginTop: 24 }}>
                 {selectedTestDoc.length > 1 && (
                   <div style={{ background: '#f6ffed', border: '1px solid #b7eb8f', padding: '12px', borderRadius: '6px' }}>
                     <Space>
                       <CheckCircleOutlined style={{ color: '#52c41a' }} />
                       <Text>已选择文档ID: {selectedTestDoc[1]}</Text>
                     </Space>
                   </div>
                 )}
              </div>
            </Form>
          </div>
        );
      case 1: // 策略配置
        return (
          <div style={{ padding: '24px 0', minHeight: '200px' }}>
            <Form layout="vertical">
              <Form.Item label="召回策略" required>
                <Radio.Group 
                  value={testStrategy} 
                  onChange={e => setTestStrategy(e.target.value)}
                  optionType="button"
                  buttonStyle="solid"
                  style={{ width: '100%' }}
                >
                  <Radio.Button value={RetrievalStrategy.HYBRID} style={{ width: '33%', textAlign: 'center' }}>混合检索</Radio.Button>
                  <Radio.Button value={RetrievalStrategy.FULL_TEXT} style={{ width: '33%', textAlign: 'center' }}>全文检索</Radio.Button>
                  <Radio.Button value={RetrievalStrategy.VECTOR} style={{ width: '33%', textAlign: 'center' }}>向量检索</Radio.Button>
                </Radio.Group>
                <div style={{ marginTop: 8, color: '#888', fontSize: '12px' }}>
                  {testStrategy === RetrievalStrategy.HYBRID && '同时使用关键词匹配和向量语义匹配，结果最全面'}
                  {testStrategy === RetrievalStrategy.FULL_TEXT && '仅使用关键词匹配，适合精确查找'}
                  {testStrategy === RetrievalStrategy.VECTOR && '仅使用向量语义匹配，适合模糊查找'}
                </div>
              </Form.Item>
              
              <Form.Item label="返回条数 (Limit)" required>
                <InputNumber 
                  min={1} 
                  max={20} 
                  value={testLimit} 
                  onChange={setTestLimit} 
                  style={{ width: '100%' }}
                />
              </Form.Item>
            </Form>
          </div>
        );
      case 2: // 测试召回
        return (
          <div style={{ padding: '24px 0', minHeight: '200px' }}>
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <Card size="small" type="inner" style={{ background: '#fafafa' }}>
                <Space split={<div style={{ width: 1, height: 16, background: '#ddd' }} />}>
                  <Text type="secondary">当前文档: <Text strong>{fileOptions.find(c=>c.value===selectedTestDoc[0])?.children?.find(f=>f.value===selectedTestDoc[1])?.label || selectedTestDoc[1]}</Text></Text>
                  <Text type="secondary">策略: <Tag color="blue">{testStrategy}</Tag></Text>
                  <Text type="secondary">Limit: {testLimit}</Text>
                </Space>
              </Card>

              <Search
                placeholder="输入测试 Query，例如：'如何申请休假'"
                allowClear
                enterButton={<Button type="primary" icon={<SearchOutlined />}>测试召回</Button>}
                size="large"
                value={testQuery}
                onChange={(e) => setTestQuery(e.target.value)}
                onSearch={(value) => handleTestSearch(value)}
                loading={isTesting}
              />

              {/* 结果展示 */}
              <List
                header={
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text strong>召回结果 ({testResults.length})</Text>
                  </div>
                }
                bordered
                dataSource={testResults}
                renderItem={(item) => (
                  <List.Item>
                    <div style={{ width: '100%' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                        <Text strong style={{ color: '#1890ff' }}>{item.file_name}</Text>
                        <Tag color={(typeof item.score === 'number' ? item.score : 0) > 0.7 ? 'green' : (typeof item.score === 'number' ? item.score : 0) > 0.4 ? 'orange' : 'red'}>
                          相似度: {(((typeof item.score === 'number' ? item.score : 0)) * 100).toFixed(2)}%
                        </Tag>
                      </div>
                      <div style={{ 
                        background: '#f5f5f5', 
                        padding: '12px', 
                        borderRadius: '6px',
                        fontSize: '13px',
                        color: '#666',
                        lineHeight: '1.6'
                      }}>
                        <Paragraph ellipsis={{ rows: 3, expandable: true, symbol: '展开' }} style={{ margin: 0 }}>
                          {item.content}
                        </Paragraph>
                      </div>
                    </div>
                  </List.Item>
                )}
              />
            </Space>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="knowledge-base-container" style={{ height: 'calc(100vh - 100px)' }}>
      <div className="page-header" style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2} style={{ margin: 0, color: 'var(--text-primary)' }}>知识库管理</Title>
        <Button 
          type="primary" 
          icon={<ExperimentOutlined />} 
          onClick={() => setIsTestModalVisible(true)}
        >
          召回测试
        </Button>
      </div>

      <Layout style={{ height: '100%', background: '#fff', border: '1px solid #f0f0f0', borderRadius: '8px', overflow: 'hidden' }}>
        {/* 左侧分类栏 */}
        <Sider width={250} theme="light" style={{ borderRight: '1px solid #f0f0f0' }}>
          <div style={{ padding: '16px', borderBottom: '1px solid #f0f0f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text strong>知识库分类</Text>
            <Tooltip title="新建分类">
              <Button 
                type="text" 
                icon={<PlusOutlined />} 
                size="small" 
                onClick={() => setIsCategoryModalVisible(true)}
              />
            </Tooltip>
          </div>
          <Menu
            mode="inline"
            selectedKeys={[selectedCategoryId]}
            style={{ borderRight: 0 }}
            onClick={({ key }) => setSelectedCategoryId(key)}
            items={categories.map(cat => ({
              key: cat.id,
              icon: <FolderOutlined />,
              label: (
                <Tooltip title={cat.description || '暂无描述'} placement="right" mouseEnterDelay={0.5}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%' }}>
                    <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', marginRight: 8 }}>{cat.name}</span>
                    <Badge count={cat.count} style={{ backgroundColor: '#f5f5f5', color: '#999', boxShadow: 'none' }} />
                  </div>
                </Tooltip>
              )
            }))}
          />
        </Sider>

        {/* 右侧内容区 */}
        <Content style={{ padding: '24px', overflowY: 'auto' }}>
          {selectedCategoryId ? (
            <>
              <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Title level={4} style={{ margin: 0 }}>
                  {categories.find(c => c.id === selectedCategoryId)?.name || '文件列表'}
                </Title>
                <Space>
                  <Button 
                    danger 
                    icon={<DeleteOutlined />} 
                    onClick={handleDeleteCategory}
                  >
                    删除分类
                  </Button>
                  <Tooltip title="支持 PDF, Markdown, Word, TXT 等格式文档">
                    <Upload 
                      beforeUpload={handleUpload} 
                      showUploadList={false}
                      disabled={uploading}
                    >
                      <Button type="primary" icon={uploading ? <LoadingOutlined /> : <UploadOutlined />}>
                        {uploading ? '上传中...' : '上传文件'}
                      </Button>
                    </Upload>
                  </Tooltip>
                </Space>
              </div>

              <Table 
                columns={columns} 
                dataSource={files} 
                rowKey="file_id" 
                loading={loadingFiles}
                pagination={false}
              />
            </>
          ) : (
            <Empty description="请选择或创建一个知识库分类" style={{ marginTop: '100px' }} />
          )}
        </Content>
      </Layout>

      {/* 新建分类弹窗 */}
      <Modal
        title="新建知识库分类"
        open={isCategoryModalVisible}
        onOk={handleCreateCategory}
        confirmLoading={creatingCategory}
        onCancel={() => setIsCategoryModalVisible(false)}
      >
        <Form layout="vertical">
          <Form.Item label="分类名称" required>
            <Input 
              placeholder="请输入分类名称，如：产品文档" 
              value={newCategoryName}
              onChange={e => setNewCategoryName(e.target.value)}
            />
          </Form.Item>
          <Form.Item label="描述">
            <Input.TextArea 
              placeholder="简要概述当前知识库所包含的知识内容" 
              value={newCategoryDesc}
              onChange={e => setNewCategoryDesc(e.target.value)}
              rows={3}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* 召回测试弹窗 (Step 模式) */}
      <Modal
        title={
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ExperimentOutlined />
            <span>召回效果测试</span>
          </div>
        }
        open={isTestModalVisible}
        onCancel={() => {
          setIsTestModalVisible(false);
          setTestResults([]);
          setTestQuery('');
          setCurrentStep(0);
        }}
        width={800}
        destroyOnClose
        footer={
          <div style={{ marginTop: 24, textAlign: 'right' }}>
            {currentStep > 0 && (
              <Button style={{ margin: '0 8px' }} onClick={() => setCurrentStep(currentStep - 1)}>
                上一步
              </Button>
            )}
            {currentStep < 2 && (
              <Button 
                type="primary" 
                onClick={() => setCurrentStep(currentStep + 1)}
                disabled={currentStep === 0 && selectedTestDoc.length < 2}
              >
                下一步
              </Button>
            )}
            {currentStep === 2 && (
              <Button type="primary" onClick={() => setIsTestModalVisible(false)}>
                完成
              </Button>
            )}
          </div>
        }
      >
        <Steps 
          current={currentStep} 
          items={[
            { title: '选择文档', description: '选择需要测试的文档' },
            { title: '策略配置', description: '设定召回方式与数量' },
            { title: '测试召回', description: '输入问题并验证' },
          ]}
          style={{ marginBottom: 24, marginTop: 12 }}
        />
        
        <div style={{ minHeight: '300px' }}>
          {renderStepContent()}
        </div>
      </Modal>
    </div>
  );
};

export default KnowledgeBase;
