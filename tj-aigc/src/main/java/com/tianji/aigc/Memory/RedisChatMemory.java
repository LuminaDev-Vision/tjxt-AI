package com.tianji.aigc.Memory;

import cn.hutool.json.JSONUtil;
import com.tianji.common.utils.CollUtils;
import jakarta.annotation.Resource;
import org.springframework.ai.chat.memory.ChatMemory;
import org.springframework.ai.chat.messages.Message;
import org.springframework.data.redis.core.StringRedisTemplate;

import java.util.List;

public class RedisChatMemory implements ChatMemory {

    private static final String DEFAULT_PREFIX = "chat:";

    private final String prefix;

    public RedisChatMemory() {
        this.prefix = DEFAULT_PREFIX;
    }

    public RedisChatMemory(String prefix) {
        this.prefix = prefix;
    }

    @Resource
    private  StringRedisTemplate stringRedisTemplate;



    @Override
    public void add(String conversationId, List<Message> messages) {
        if(CollUtils.isEmpty(messages) ){
            return;
        }
        var key = this.getKey(conversationId);
        var listOps = this.stringRedisTemplate.boundListOps(key); // 绑定到一个 List 类型的 key
        messages.forEach(message -> {
            listOps.rightPush(JSONUtil.toJsonStr(message)); // 将消息序列化为 JSON 字符串并添加到 List 的右侧
        });
    }

    private String getKey(String conversationId) {
        return prefix + conversationId;
    }

    @Override
    public List<Message> get(String conversationId, int lastN) {
        // 暂时不实现
        return List.of();
    }

    @Override
    public void clear(String conversationId) {
        stringRedisTemplate.delete(prefix + conversationId);
    }
}
