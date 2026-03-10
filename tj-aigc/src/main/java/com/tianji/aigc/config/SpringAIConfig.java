package com.tianji.aigc.config;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.chat.client.advisor.SimpleLoggerAdvisor;
import org.springframework.ai.chat.client.advisor.api.Advisor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class SpringAIConfig {

    /**
     * 配置ChatClient
     */
    @Bean
    public ChatClient chatClient(ChatClient.Builder builder, Advisor loggerAdvisor) {
        return builder.defaultAdvisors(loggerAdvisor).build();
    }

    /**
     * 日志记录器
     */
    @Bean
    public Advisor loggerAdvisor(){
        return new SimpleLoggerAdvisor();
    }
}
