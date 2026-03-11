package com.tianji.aigc.config;

import com.tianji.aigc.memory.RedisChatMemory;
import com.tianji.aigc.tools.CourseTools;
import com.tianji.aigc.tools.OrderTools;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.MessageChatMemoryAdvisor;
import org.springframework.ai.chat.client.advisor.SimpleLoggerAdvisor;
import org.springframework.ai.chat.client.advisor.api.Advisor;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SpringAIConfig {

    /**
     * 配置ChatClient
     */
    @Bean
    public ChatClient chatClient(ChatClient.Builder builder,
                                 Advisor loggerAdvisor, //日志记录器
                                 Advisor messageChatMemoryAdvisor, //基于Redis的会话记忆，聊天记忆整合到system message中实现多轮对话
                                 CourseTools courseTools, // 课程工具类
                                 OrderTools orderTools // 订单工具类
     )
    {
        return builder
                .defaultAdvisors(loggerAdvisor,messageChatMemoryAdvisor) //添加 Advisor 功能增强
                .defaultTools(courseTools,orderTools) //添加工具类
                .build();
    }

    /**
     * 日志记录器
     */
    @Bean
    public Advisor loggerAdvisor(){
        return new SimpleLoggerAdvisor();
    }

    /**
     * 配置ChatMemory
     */
    @Bean
    public ChatMemory chatMemory(){
        return new RedisChatMemory();
    }

    /**
     * 基于Redis的会话记忆，聊天记忆整合到system message中实现多轮对话
     */
    @Bean
    public Advisor messageChatMemoryAdvisor(ChatMemory chatMemory){
        return new MessageChatMemoryAdvisor(chatMemory);
    }
}
