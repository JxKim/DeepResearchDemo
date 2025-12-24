from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import List, Optional

#内部依赖
from routes.utils import get_current_user_from_token
from services.knowledge_service import knowledge_service
from routes.schema import (
    KnowledgeFileListResponse,
    KnowledgeCategoryListResponse,
    KnowledgeCategoryCreate,
    KnowledgeCategory,
    KnowledgeFile,
    BaseResponse,
    ParseProgress,
    ParseProgressResponse,
    RecallTestRequest,
    RecallTestResponse,
    RecallResult
)
from db.database import get_db

router = APIRouter(prefix="/knowledge", tags=["知识库管理"])



@router.post("/upload", response_model=BaseResponse)
async def upload_file(file: UploadFile = File(...), category_id:str=Form(...),current_user=Depends(get_current_user_from_token),db=Depends(get_db)):
    """
    上传文件到知识库,通过opendal存储文件
    支持类型为pdf,word, txt, csv
    """
    content = await file.read()
    new_file = await knowledge_service.upload_file(current_user.id, file.filename, content,db=db,category_id=category_id)
    return BaseResponse(
        message="上传成功",
        data=KnowledgeFile(
            file_id=new_file.id,
            file_name=new_file.file_name,
            parse_status=new_file.parse_status,
            chunk_num=new_file.chunk_count,
            user_id=new_file.user_id,
            category_id=new_file.category_id,
            created_at=new_file.created_at,
            updated_at=new_file.updated_at,
        ),
    )


@router.delete("/{file_id}", response_model=BaseResponse)
async def delete_knowledge(file_id: str,category_id:str, current_user=Depends(get_current_user_from_token),db=Depends(get_db)):
    """
    删除指定知识库
    """
    deleted = await knowledge_service.delete_file(current_user.id, category_id, file_id,db=db)
    if not deleted:
        return BaseResponse(success=False, message="文件不存在或无权限")
    return BaseResponse(message="删除成功")

@router.post("/parse/submit", response_model=BaseResponse)
async def parse_file(file_id: str, category_id:str,current_user=Depends(get_current_user_from_token),db=Depends(get_db)):
    """
    长耗时任务，需要前端实时解析，当前解析到了哪一步。解析上传的文件
    """
    file_id = await knowledge_service.submit_parse_task(current_user.id, category_id,file_id,db=db)
    if not file_id:
        return BaseResponse(success=False, message="文件不存在或无权限")
    return BaseResponse(message="解析任务提交成功", data={"file_id": file_id,"status":"processing"})



@router.get("/parse/progress/{file_id}", response_model=ParseProgressResponse)
async def get_parse_progress(file_id: str, current_user=Depends(get_current_user_from_token),db=Depends(get_db)):
    """
    获取文件解析进度
    """
    progress = await knowledge_service.get_parse_status(file_id, db=db, user_id=current_user.id)
    if not progress:
        return ParseProgressResponse(data=None)
    return ParseProgressResponse(
        data=ParseProgress(
            file_id=file_id,
            status=progress.get("status"),
            chunk_num=progress.get("chunk_count"),
            updated_at=progress.get("updated_at"),
        )
    )



@router.post("/recall/test", response_model=RecallTestResponse)
async def test_recall(request: RecallTestRequest, current_user=Depends(get_current_user_from_token)):
    """
    测试知识库召回效果
    """
    # 1. 搜索
    results = await knowledge_service.search_content(
        request.query,
        request.limit,
        search_strategy=request.search_strategy,
        file_id=request.file_id,
    )

    data_list = []
    if results:
        single_query_result = results[0]
        for single_result in single_query_result:
            data_list.append(
                RecallResult(
                    file_name=single_result.get("file_name"),
                    content=single_result.get("text"),
                    score=single_result.get("score"),
                )
            )
        
    return RecallTestResponse(data=data_list)

@router.post("/category", response_model=KnowledgeCategory)
async def create_category(
    category: KnowledgeCategoryCreate,
    current_user=Depends(get_current_user_from_token), 
    db=Depends(get_db)
):
    """
    创建知识库类别
    """
    try:
        new_category = await knowledge_service.create_category(current_user.id, category.name, category.description, db=db)
        return KnowledgeCategory(id=new_category.id, name=new_category.name, description=new_category.description, count=0)
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/category/{category_id}", response_model=BaseResponse)
async def delete_category(category_id: str, current_user=Depends(get_current_user_from_token), db=Depends(get_db)):
    deleted = await knowledge_service.delete_category(current_user.id, category_id, db=db)
    if not deleted:
        return BaseResponse(success=False, message="分类不存在或无权限")
    return BaseResponse(message="删除成功")

@router.get("/categories", response_model=KnowledgeCategoryListResponse)
async def get_all_categories(current_user=Depends(get_current_user_from_token),db=Depends(get_db)):
    """
    获取所有知识库类别
    """
    categories_with_counts = await knowledge_service.get_all_categories(current_user.id,db=db)
    data = []
    for category, count in categories_with_counts:
        data.append(
            KnowledgeCategory(
                id=category.id,
                name=category.name,
                description=category.description,
                count=count or 0,
            )
        )
    return KnowledgeCategoryListResponse(data=data)

@router.get("/category/{category_id}/files", response_model=KnowledgeFileListResponse)
async def get_files_by_category(category_id: str, current_user=Depends(get_current_user_from_token), db=Depends(get_db)):
    """
    获取指定类别的所有文件
    """
    file_records = await knowledge_service.get_files_by_category(current_user.id, category_id, db=db)
    data = []
    for file_record in file_records or []:
        data.append(
            KnowledgeFile(
                file_id=file_record.id,
                file_name=file_record.file_name,
                parse_status=file_record.parse_status,
                chunk_num=file_record.chunk_count,
                user_id=file_record.user_id,
                category_id=file_record.category_id,
                created_at=file_record.created_at,
                updated_at=file_record.updated_at,
            )
        )
    return KnowledgeFileListResponse(data=data)
