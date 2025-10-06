"""
RAG (Retrieval-Augmented Generation) 系统
用于从秋招数据中检索相关信息并增强AI回复
"""
import json
import os
import re
from typing import List, Dict, Any, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class RAGSystem:
    def __init__(self, data_path: str = None):
        """
        初始化RAG系统
        
        Args:
            data_path: 数据文件路径，默认为autumn/data.json
        """
        if data_path is None:
            # 默认路径
            current_dir = Path(__file__).parent
            data_path = current_dir.parent / 'autumn' / 'data.json'
        
        self.data_path = Path(data_path)
        self.job_data = self._load_job_data()
        
    def _load_job_data(self) -> List[Dict[str, Any]]:
        """加载职位数据"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 提取所有职位数据
            jobs = []
            if '_default' in data:
                for job_id, job_info in data['_default'].items():
                    job_info['id'] = job_id
                    jobs.append(job_info)
            
            logger.info(f"成功加载 {len(jobs)} 个职位数据")
            return jobs
            
        except Exception as e:
            logger.error(f"加载职位数据失败: {str(e)}")
            return []
    
    def _preprocess_text(self, text: str) -> str:
        """预处理文本，提取关键词"""
        if not text:
            return ""
        
        # 清理文本
        text = re.sub(r'\r\n', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def _create_job_document(self, job: Dict[str, Any]) -> str:
        """将职位信息转换为文档格式"""
        doc_parts = []
        
        # 公司名称
        if job.get('company'):
            doc_parts.append(f"公司：{job['company']}")
        
        # 职位名称
        if job.get('position'):
            doc_parts.append(f"职位：{job['position']}")
        
        # 状态
        if job.get('status'):
            doc_parts.append(f"状态：{job['status']}")
        
        # 详细说明
        if job.get('note'):
            note = self._preprocess_text(job['note'])
            doc_parts.append(f"职位详情：{note}")
        
        # URL
        if job.get('url'):
            doc_parts.append(f"链接：{job['url']}")
        
        return " | ".join(doc_parts)
    
    def _calculate_similarity(self, query: str, document: str) -> float:
        """
        计算查询和文档的相似度
        使用简单的关键词匹配和TF-IDF思想
        """
        if not query or not document:
            return 0.0
        
        query_words = set(re.findall(r'[\u4e00-\u9fff\w]+', query.lower()))
        doc_words = set(re.findall(r'[\u4e00-\u9fff\w]+', document.lower()))
        
        if not query_words:
            return 0.0
        
        # 计算交集
        intersection = query_words.intersection(doc_words)
        
        # 计算相似度分数
        similarity = len(intersection) / len(query_words)
        
        # 添加长度惩罚，避免过长的文档得分过高
        length_penalty = min(1.0, 100 / len(document))
        
        return similarity * length_penalty
    
    def retrieve_relevant_jobs(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        检索与查询相关的职位信息
        
        Args:
            query: 用户查询
            top_k: 返回最相关的k个职位
            
        Returns:
            相关职位列表，按相似度排序
        """
        if not self.job_data:
            return []
        
        # 计算每个职位的相似度
        job_scores = []
        for job in self.job_data:
            document = self._create_job_document(job)
            similarity = self._calculate_similarity(query, document)
            
            if similarity > 0:  # 只保留有相关性的职位
                job_scores.append((job, similarity))
        
        # 按相似度排序
        job_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 返回top_k个最相关的职位
        return [job for job, score in job_scores[:top_k]]
    
    def format_context_for_ai(self, relevant_jobs: List[Dict[str, Any]]) -> str:
        """
        将相关职位信息格式化为AI可用的上下文
        
        Args:
            relevant_jobs: 相关职位列表
            
        Returns:
            格式化的上下文字符串
        """
        if not relevant_jobs:
            return "暂无相关职位信息。"
        
        context_parts = ["以下是相关的秋招职位信息："]
        
        for i, job in enumerate(relevant_jobs, 1):
            context_parts.append(f"\n{i}. {job.get('company', '未知公司')} - {job.get('position', '未知职位')}")
            context_parts.append(f"   状态：{job.get('status', '未知')}")
            
            if job.get('note'):
                note = self._preprocess_text(job['note'])
                # 截取前200个字符避免上下文过长
                if len(note) > 200:
                    note = note[:200] + "..."
                context_parts.append(f"   详情：{note}")
            
            if job.get('url'):
                context_parts.append(f"   链接：{job['url']}")
        
        return "\n".join(context_parts)
    
    def get_context_for_query(self, query: str, top_k: int = 3) -> str:
        """
        为查询获取相关上下文
        
        Args:
            query: 用户查询
            top_k: 返回最相关的k个职位
            
        Returns:
            格式化的上下文字符串
        """
        relevant_jobs = self.retrieve_relevant_jobs(query, top_k)
        return self.format_context_for_ai(relevant_jobs)
    
    def get_all_companies(self) -> List[str]:
        """获取所有公司名称"""
        companies = set()
        for job in self.job_data:
            if job.get('company'):
                companies.add(job['company'])
        return sorted(list(companies))
    
    def get_all_positions(self) -> List[str]:
        """获取所有职位名称"""
        positions = set()
        for job in self.job_data:
            if job.get('position'):
                positions.add(job['position'])
        return sorted(list(positions))
    
    def search_by_company(self, company: str) -> List[Dict[str, Any]]:
        """根据公司名称搜索职位"""
        results = []
        for job in self.job_data:
            if job.get('company') and company.lower() in job['company'].lower():
                results.append(job)
        return results
    
    def search_by_position(self, position: str) -> List[Dict[str, Any]]:
        """根据职位名称搜索"""
        results = []
        for job in self.job_data:
            if job.get('position') and position.lower() in job['position'].lower():
                results.append(job)
        return results
