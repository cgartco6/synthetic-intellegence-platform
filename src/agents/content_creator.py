import asyncio
import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent, Task, SyntheticIntelligenceMixin
from ..models.llm_wrapper import LLMWrapper
from ..helpers.file_processor import FileProcessor

class ContentCreatorAgent(BaseAgent, SyntheticIntelligenceMixin):
    def __init__(self, config: Dict[str, Any] = None):
        capabilities = [
            'blog_post', 'social_media_post', 'email_newsletter',
            'video_script', 'ad_copy', 'product_description',
            'content_optimization', 'seo_analysis'
        ]
        super().__init__('content_creator', capabilities, config)
        
        self.llm = LLMWrapper(config.get('llm', {}))
        self.file_processor = FileProcessor()
        self.content_templates = self._load_templates()
        
    def _load_templates(self) -> Dict[str, Any]:
        return {
            'blog_post': {
                'structure': ['title', 'introduction', 'body', 'conclusion'],
                'tone_options': ['professional', 'casual', 'technical', 'conversational']
            },
            'social_media_post': {
                'platforms': ['facebook', 'instagram', 'twitter', 'linkedin', 'tiktok'],
                'max_lengths': {
                    'twitter': 280,
                    'facebook': 5000,
                    'instagram': 2200,
                    'linkedin': 3000,
                    'tiktok': 150
                }
            }
        }
    
    async def execute(self, task: Task) -> Task:
        if task.type == 'blog_post':
            return await self._create_blog_post(task)
        elif task.type == 'social_media_post':
            return await self._create_social_media_post(task)
        elif task.type == 'video_script':
            return await self._create_video_script(task)
        elif task.type == 'content_optimization':
            return await self._optimize_content(task)
        else:
            task.error = f"Unsupported task type: {task.type}"
            return task
    
    async def _create_blog_post(self, task: Task) -> Task:
        payload = task.payload
        topic = payload.get('topic', '')
        tone = payload.get('tone', 'professional')
        length = payload.get('length', 'medium')
        keywords = payload.get('keywords', [])
        
        prompt = f"""
        Create a comprehensive blog post with the following requirements:
        Topic: {topic}
        Tone: {tone}
        Length: {length}
        Keywords: {', '.join(keywords)}
        
        Please structure the post with:
        1. Engaging title
        2. Introduction that hooks the reader
        3. Main body with clear sections
        4. Conclusion with key takeaways
        5. Call-to-action
        
        Make sure the content is original, well-researched, and optimized for SEO.
        """
        
        try:
            content = await self.llm.generate_text(prompt)
            
            # Generate multiple title options
            title_prompt = f"Generate 5 engaging titles for a blog post about: {topic}"
            titles = await self.llm.generate_text(title_prompt)
            
            # SEO optimization
            seo_analysis = await self._analyze_seo(content, keywords)
            
            task.result = {
                'content': content,
                'titles': titles.split('\n'),
                'seo_analysis': seo_analysis,
                'word_count': len(content.split()),
                'reading_time': f"{len(content.split()) // 200} minutes"
            }
            
        except Exception as e:
            task.error = f"Failed to create blog post: {str(e)}"
        
        return task
    
    async def _create_social_media_post(self, task: Task) -> Task:
        payload = task.payload
        platform = payload.get('platform', 'facebook')
        topic = payload.get('topic', '')
        tone = payload.get('tone', 'casual')
        include_hashtags = payload.get('include_hashtags', True)
        include_emoji = payload.get('include_emoji', True)
        
        max_length = self.content_templates['social_media_post']['max_lengths'].get(platform, 280)
        
        prompt = f"""
        Create a {platform} post about: {topic}
        Tone: {tone}
        Maximum length: {max_length} characters
        Include hashtags: {include_hashtags}
        Include emojis: {include_emoji}
        
        Make it engaging and platform-appropriate.
        """
        
        try:
            post_content = await self.llm.generate_text(prompt)
            
            # Generate multiple variations
            variations_prompt = f"Create 3 variations of this post with different angles:\n{post_content}"
            variations = await self.llm.generate_text(variations_prompt)
            
            task.result = {
                'platform': platform,
                'content': post_content,
                'variations': variations.split('\n'),
                'character_count': len(post_content),
                'hashtags': await self._extract_hashtags(post_content) if include_hashtags else []
            }
            
        except Exception as e:
            task.error = f"Failed to create social media post: {str(e)}"
        
        return task
    
    async def _create_video_script(self, task: Task) -> Task:
        payload = task.payload
        topic = payload.get('topic', '')
        duration = payload.get('duration', 5)  # minutes
        style = payload.get('style', 'educational')
        
        prompt = f"""
        Create a video script with the following requirements:
        Topic: {topic}
        Duration: {duration} minutes
        Style: {style}
        
        Include:
        1. Hook (first 15 seconds)
        2. Main content with timestamps
        3. Visual descriptions
        4. Voiceover script
        5. Call-to-action
        
        Format as a structured script with timecodes.
        """
        
        try:
            script = await self.llm.generate_text(prompt)
            
            task.result = {
                'script': script,
                'estimated_duration': f"{duration} minutes",
                'sections': await self._parse_script_sections(script),
                'visual_cues': await self._extract_visual_cues(script)
            }
            
        except Exception as e:
            task.error = f"Failed to create video script: {str(e)}"
        
        return task
    
    async def _optimize_content(self, task: Task) -> Task:
        payload = task.payload
        content = payload.get('content', '')
        target_keywords = payload.get('keywords', [])
        
        analysis_prompt = f"""
        Analyze and optimize this content for better engagement and SEO:
        
        Content: {content}
        Target Keywords: {', '.join(target_keywords)}
        
        Provide:
        1. SEO score (1-100)
        2. Readability analysis
        3. Suggested improvements
        4. Optimized version
        5. Keyword density analysis
        """
        
        try:
            analysis = await self.llm.generate_text(analysis_prompt)
            
            task.result = {
                'original_content': content,
                'optimized_content': analysis,
                'analysis': await self._parse_optimization_analysis(analysis),
                'keyword_density': await self._calculate_keyword_density(content, target_keywords)
            }
            
        except Exception as e:
            task.error = f"Failed to optimize content: {str(e)}"
        
        return task
    
    async def _analyze_seo(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Analyze SEO metrics for content"""
        # Simplified SEO analysis
        word_count = len(content.split())
        keyword_density = await self._calculate_keyword_density(content, keywords)
        
        return {
            'word_count': word_count,
            'keyword_density': keyword_density,
            'readability_score': await self._calculate_readability(content),
            'recommendations': await self._generate_seo_recommendations(content, keywords)
        }
    
    async def _calculate_keyword_density(self, content: str, keywords: List[str]) -> Dict[str, float]:
        """Calculate keyword density"""
        words = content.lower().split()
        total_words = len(words)
        density = {}
        
        for keyword in keywords:
            keyword_count = content.lower().count(keyword.lower())
            density[keyword] = (keyword_count / total_words * 100) if total_words > 0 else 0
        
        return density
    
    async def _calculate_readability(self, content: str) -> float:
        """Calculate readability score (simplified)"""
        # Simplified Flesch Reading Ease approximation
        sentences = content.split('.')
        words = content.split()
        
        if len(sentences) == 0 or len(words) == 0:
            return 0
        
        avg_sentence_length = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Very simplified calculation
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * (avg_word_length / 100))
        return max(0, min(100, score))
    
    async def _generate_seo_recommendations(self, content: str, keywords: List[str]) -> List[str]:
        """Generate SEO recommendations"""
        recommendations = []
        
        if len(content.split()) < 300:
            recommendations.append("Consider increasing content length for better SEO")
        
        # Check for keyword usage
        for keyword in keywords:
            if keyword.lower() not in content.lower():
                recommendations.append(f"Add keyword: {keyword}")
        
        return recommendations
    
    async def _extract_hashtags(self, content: str) -> List[str]:
        """Extract or generate relevant hashtags"""
        prompt = f"Generate 5-10 relevant hashtags for this content:\n{content}"
        hashtags_text = await self.llm.generate_text(prompt)
        return [tag.strip() for tag in hashtags_text.split('\n') if tag.strip()]
    
    async def _parse_script_sections(self, script: str) -> List[Dict[str, str]]:
        """Parse script into sections with timestamps"""
        # Simplified parsing - in real implementation, use more sophisticated parsing
        lines = script.split('\n')
        sections = []
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('[') and ']' in line:
                if current_section:
                    sections.append(current_section)
                current_section = {'timestamp': line, 'content': ''}
            elif current_section and line:
                current_section['content'] += line + ' '
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    async def _extract_visual_cues(self, script: str) -> List[str]:
        """Extract visual cues from script"""
        prompt = f"Extract all visual cues and scene descriptions from this script:\n{script}"
        visual_cues = await self.llm.generate_text(prompt)
        return [cue.strip() for cue in visual_cues.split('\n') if cue.strip()]
    
    async def _parse_optimization_analysis(self, analysis: str) -> Dict[str, Any]:
        """Parse optimization analysis into structured data"""
        # Simplified parsing
        return {
            'raw_analysis': analysis,
            'summary': await self._extract_summary(analysis),
            'improvements': await self._extract_improvements(analysis)
        }
    
    async def _extract_summary(self, analysis: str) -> str:
        """Extract summary from analysis"""
        # Simplified extraction
        lines = analysis.split('\n')
        return lines[0] if lines else ""
    
    async def _extract_improvements(self, analysis: str) -> List[str]:
        """Extract improvement suggestions from analysis"""
        # Simplified extraction
        lines = analysis.split('\n')
        improvements = []
        
        for line in lines:
            if any(marker in line.lower() for marker in ['suggest', 'improve', 'recommend', 'consider']):
                improvements.append(line.strip())
        
        return improvements
