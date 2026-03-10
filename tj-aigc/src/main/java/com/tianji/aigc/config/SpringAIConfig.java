package com.tianji.aigc.config;

import com.tianji.aigc.Memory.RedisChatMemory;
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
                                 Advisor loggerAdvisor,
                                 Advisor messageChatMemoryAdvisor) {
        return builder
                .defaultAdvisors(loggerAdvisor,messageChatMemoryAdvisor)
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
