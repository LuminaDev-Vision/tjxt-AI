package com.tianji.aigc.memory;


import lombok.Data;

import org.springframework.ai.chat.messages.AssistantMessage;
import org.springframework.ai.chat.messages.ToolResponseMessage;
import org.springframework.ai.model.Media;

import java.util.List;
import java.util.Map;

/**
 * Redis存储的消息对象，用于序列化和反序列化
 */
@Data
public class RedisMessage {

    private String messageType;
    private Map<String, Object> metadata = Map.of();
    private List<Media> media = List.of();
    private List<AssistantMessage.ToolCall> toolCalls = List.of();
    private String textContent;
    private List<ToolResponseMessage.ToolResponse> toolResponses = List.of();
    private Map<String, Object> params = Map.of();


    private Map<String, Object> properties = Map.of();
}
