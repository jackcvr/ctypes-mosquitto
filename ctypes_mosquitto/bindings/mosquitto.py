# script is auto-generated

"""Usage example:
import ctypes as C

from . import bind, bind_all

lib = ...


class CType:
    int_p = C.c_void_p
    mosquitto_p = C.c_void_p
    mosquitto_property_p = C.c_void_p
    char_pp = C.c_void_p
    mosquitto_message_p = C.c_void_p
    mosquitto_message_pp = C.c_void_p
    mosq_opt_t = ...
    char_ppp = C.c_void_p
    bool_p = C.c_void_p
    libmosquitto_will_p = C.c_void_p
    libmosquitto_tls_p = C.c_void_p
    mosquitto_property_pp = C.c_void_p
    uint8_t_p = C.c_void_p
    uint16_t_p = C.c_void_p
    uint32_t_p = C.c_void_p
    void_pp = C.c_void_p


bind_all(lib, CType)

# void mosquitto_message_callback_set(struct mosquitto *mosq, void (*on_message)(struct mosquitto *, void *, const struct mosquitto_message *));
bind(None, lib.mosquitto_message_callback_set, ...)
# void mosquitto_connect_with_flags_callback_set(struct mosquitto *mosq, void (*on_connect)(struct mosquitto *, void *, int, int));
bind(None, lib.mosquitto_connect_with_flags_callback_set, ...)
# int mosquitto_tls_set(struct mosquitto *mosq, const char *cafile, const char *capath, const char *certfile, const char *keyfile, int (*pw_callback)(char *buf, int size, int rwflag, void *userdata));
bind(C.c_int, lib.mosquitto_tls_set, ...)
# void mosquitto_publish_v5_callback_set(struct mosquitto *mosq, void (*on_publish)(struct mosquitto *, void *, int, int, const mosquitto_property *props));
bind(None, lib.mosquitto_publish_v5_callback_set, ...)
# void mosquitto_subscribe_v5_callback_set(struct mosquitto *mosq, void (*on_subscribe)(struct mosquitto *, void *, int, int, const int *, const mosquitto_property *props));
bind(None, lib.mosquitto_subscribe_v5_callback_set, ...)
# void mosquitto_unsubscribe_callback_set(struct mosquitto *mosq, void (*on_unsubscribe)(struct mosquitto *, void *, int));
bind(None, lib.mosquitto_unsubscribe_callback_set, ...)
# void mosquitto_connect_v5_callback_set(struct mosquitto *mosq, void (*on_connect)(struct mosquitto *, void *, int, int, const mosquitto_property *props));
bind(None, lib.mosquitto_connect_v5_callback_set, ...)
# void mosquitto_publish_callback_set(struct mosquitto *mosq, void (*on_publish)(struct mosquitto *, void *, int));
bind(None, lib.mosquitto_publish_callback_set, ...)
# void mosquitto_disconnect_callback_set(struct mosquitto *mosq, void (*on_disconnect)(struct mosquitto *, void *, int));
bind(None, lib.mosquitto_disconnect_callback_set, ...)
# void mosquitto_message_v5_callback_set(struct mosquitto *mosq, void (*on_message)(struct mosquitto *, void *, const struct mosquitto_message *, const mosquitto_property *props));
bind(None, lib.mosquitto_message_v5_callback_set, ...)
# void mosquitto_subscribe_callback_set(struct mosquitto *mosq, void (*on_subscribe)(struct mosquitto *, void *, int, int, const int *));
bind(None, lib.mosquitto_subscribe_callback_set, ...)
# int mosquitto_subscribe_callback( int (*callback)(struct mosquitto *, void *, const struct mosquitto_message *), void *userdata, const char *topic, int qos, const char *host, int port, const char *client_id, int keepalive, bool clean_session, const char *username, const char *password, const struct libmosquitto_will *will, const struct libmosquitto_tls *tls);
bind(C.c_int, lib.mosquitto_subscribe_callback, ...)
# void mosquitto_unsubscribe_v5_callback_set(struct mosquitto *mosq, void (*on_unsubscribe)(struct mosquitto *, void *, int, const mosquitto_property *props));
bind(None, lib.mosquitto_unsubscribe_v5_callback_set, ...)
# void mosquitto_disconnect_v5_callback_set(struct mosquitto *mosq, void (*on_disconnect)(struct mosquitto *, void *, int, const mosquitto_property *props));
bind(None, lib.mosquitto_disconnect_v5_callback_set, ...)
# void mosquitto_log_callback_set(struct mosquitto *mosq, void (*on_log)(struct mosquitto *, void *, int, const char *));
bind(None, lib.mosquitto_log_callback_set, ...)
# void mosquitto_connect_callback_set(struct mosquitto *mosq, void (*on_connect)(struct mosquitto *, void *, int));
bind(None, lib.mosquitto_connect_callback_set, ...)

"""

import ctypes as C


def bind(restype, func, *argtypes):
    func.restype = restype
    func.argtypes = argtypes


def bind_all(lib, ctx):
    # int mosquitto_lib_version(int *major, int *minor, int *revision);
    bind(C.c_int, lib.mosquitto_lib_version, ctx.int_p, ctx.int_p, ctx.int_p)
    # int mosquitto_lib_init(void);
    bind(C.c_int, lib.mosquitto_lib_init)
    # int mosquitto_lib_cleanup(void);
    bind(C.c_int, lib.mosquitto_lib_cleanup)
    # struct mosquitto *mosquitto_new(const char *id, bool clean_session, void *obj);
    bind(ctx.mosquitto_p, lib.mosquitto_new, C.c_char_p, C.c_bool, C.c_void_p)
    # void mosquitto_destroy(struct mosquitto *mosq);
    bind(None, lib.mosquitto_destroy, ctx.mosquitto_p)
    # int mosquitto_reinitialise(struct mosquitto *mosq, const char *id, bool clean_session, void *obj);
    bind(
        C.c_int,
        lib.mosquitto_reinitialise,
        ctx.mosquitto_p,
        C.c_char_p,
        C.c_bool,
        C.c_void_p,
    )
    # int mosquitto_will_set(struct mosquitto *mosq, const char *topic, int payloadlen, const void *payload, int qos, bool retain);
    bind(
        C.c_int,
        lib.mosquitto_will_set,
        ctx.mosquitto_p,
        C.c_char_p,
        C.c_int,
        C.c_void_p,
        C.c_int,
        C.c_bool,
    )
    # int mosquitto_will_set_v5(struct mosquitto *mosq, const char *topic, int payloadlen, const void *payload, int qos, bool retain, mosquitto_property *properties);
    bind(
        C.c_int,
        lib.mosquitto_will_set_v5,
        ctx.mosquitto_p,
        C.c_char_p,
        C.c_int,
        C.c_void_p,
        C.c_int,
        C.c_bool,
        ctx.mosquitto_property_p,
    )
    # int mosquitto_will_clear(struct mosquitto *mosq);
    bind(C.c_int, lib.mosquitto_will_clear, ctx.mosquitto_p)
    # int mosquitto_username_pw_set(struct mosquitto *mosq, const char *username, const char *password);
    bind(
        C.c_int, lib.mosquitto_username_pw_set, ctx.mosquitto_p, C.c_char_p, C.c_char_p
    )
    # int mosquitto_connect(struct mosquitto *mosq, const char *host, int port, int keepalive);
    bind(C.c_int, lib.mosquitto_connect, ctx.mosquitto_p, C.c_char_p, C.c_int, C.c_int)
    # int mosquitto_connect_bind(struct mosquitto *mosq, const char *host, int port, int keepalive, const char *bind_address);
    bind(
        C.c_int,
        lib.mosquitto_connect_bind,
        ctx.mosquitto_p,
        C.c_char_p,
        C.c_int,
        C.c_int,
        C.c_char_p,
    )
    # int mosquitto_connect_bind_v5(struct mosquitto *mosq, const char *host, int port, int keepalive, const char *bind_address, const mosquitto_property *properties);
    bind(
        C.c_int,
        lib.mosquitto_connect_bind_v5,
        ctx.mosquitto_p,
        C.c_char_p,
        C.c_int,
        C.c_int,
        C.c_char_p,
        ctx.mosquitto_property_p,
    )
    # int mosquitto_connect_async(struct mosquitto *mosq, const char *host, int port, int keepalive);
    bind(
        C.c_int,
        lib.mosquitto_connect_async,
        ctx.mosquitto_p,
        C.c_char_p,
        C.c_int,
        C.c_int,
    )
    # int mosquitto_connect_bind_async(struct mosquitto *mosq, const char *host, int port, int keepalive, const char *bind_address);
    bind(
        C.c_int,
        lib.mosquitto_connect_bind_async,
        ctx.mosquitto_p,
        C.c_char_p,
        C.c_int,
        C.c_int,
        C.c_char_p,
    )
    # int mosquitto_connect_srv(struct mosquitto *mosq, const char *host, int keepalive, const char *bind_address);
    bind(
        C.c_int,
        lib.mosquitto_connect_srv,
        ctx.mosquitto_p,
        C.c_char_p,
        C.c_int,
        C.c_char_p,
    )
    # int mosquitto_reconnect(struct mosquitto *mosq);
    bind(C.c_int, lib.mosquitto_reconnect, ctx.mosquitto_p)
    # int mosquitto_reconnect_async(struct mosquitto *mosq);
    bind(C.c_int, lib.mosquitto_reconnect_async, ctx.mosquitto_p)
    # int mosquitto_disconnect(struct mosquitto *mosq);
    bind(C.c_int, lib.mosquitto_disconnect, ctx.mosquitto_p)
    # int mosquitto_disconnect_v5(struct mosquitto *mosq, int reason_code, const mosquitto_property *properties);
    bind(
        C.c_int,
        lib.mosquitto_disconnect_v5,
        ctx.mosquitto_p,
        C.c_int,
        ctx.mosquitto_property_p,
    )
    # int mosquitto_publish(struct mosquitto *mosq, int *mid, const char *topic, int payloadlen, const void *payload, int qos, bool retain);
    bind(
        C.c_int,
        lib.mosquitto_publish,
        ctx.mosquitto_p,
        ctx.int_p,
        C.c_char_p,
        C.c_int,
        C.c_void_p,
        C.c_int,
        C.c_bool,
    )
    # int mosquitto_publish_v5( struct mosquitto *mosq, int *mid, const char *topic, int payloadlen, const void *payload, int qos, bool retain, const mosquitto_property *properties);
    bind(
        C.c_int,
        lib.mosquitto_publish_v5,
        ctx.mosquitto_p,
        ctx.int_p,
        C.c_char_p,
        C.c_int,
        C.c_void_p,
        C.c_int,
        C.c_bool,
        ctx.mosquitto_property_p,
    )
    # int mosquitto_subscribe(struct mosquitto *mosq, int *mid, const char *sub, int qos);
    bind(
        C.c_int,
        lib.mosquitto_subscribe,
        ctx.mosquitto_p,
        ctx.int_p,
        C.c_char_p,
        C.c_int,
    )
    # int mosquitto_subscribe_v5(struct mosquitto *mosq, int *mid, const char *sub, int qos, int options, const mosquitto_property *properties);
    bind(
        C.c_int,
        lib.mosquitto_subscribe_v5,
        ctx.mosquitto_p,
        ctx.int_p,
        C.c_char_p,
        C.c_int,
        C.c_int,
        ctx.mosquitto_property_p,
    )
    # int mosquitto_subscribe_multiple(struct mosquitto *mosq, int *mid, int sub_count, char *const *const sub, int qos, int options, const mosquitto_property *properties);
    bind(
        C.c_int,
        lib.mosquitto_subscribe_multiple,
        ctx.mosquitto_p,
        ctx.int_p,
        C.c_int,
        ctx.char_pp,
        C.c_int,
        C.c_int,
        ctx.mosquitto_property_p,
    )
    # int mosquitto_unsubscribe(struct mosquitto *mosq, int *mid, const char *sub);
    bind(C.c_int, lib.mosquitto_unsubscribe, ctx.mosquitto_p, ctx.int_p, C.c_char_p)
    # int mosquitto_unsubscribe_v5(struct mosquitto *mosq, int *mid, const char *sub, const mosquitto_property *properties);
    bind(
        C.c_int,
        lib.mosquitto_unsubscribe_v5,
        ctx.mosquitto_p,
        ctx.int_p,
        C.c_char_p,
        ctx.mosquitto_property_p,
    )
    # int mosquitto_unsubscribe_multiple(struct mosquitto *mosq, int *mid, int sub_count, char *const *const sub, const mosquitto_property *properties);
    bind(
        C.c_int,
        lib.mosquitto_unsubscribe_multiple,
        ctx.mosquitto_p,
        ctx.int_p,
        C.c_int,
        ctx.char_pp,
        ctx.mosquitto_property_p,
    )
    # int mosquitto_message_copy(struct mosquitto_message *dst, const struct mosquitto_message *src);
    bind(
        C.c_int,
        lib.mosquitto_message_copy,
        ctx.mosquitto_message_p,
        ctx.mosquitto_message_p,
    )
    # void mosquitto_message_free(struct mosquitto_message **message);
    bind(None, lib.mosquitto_message_free, ctx.mosquitto_message_pp)
    # void mosquitto_message_free_contents(struct mosquitto_message *message);
    bind(None, lib.mosquitto_message_free_contents, ctx.mosquitto_message_p)
    # int mosquitto_loop_forever(struct mosquitto *mosq, int timeout, int max_packets);
    bind(C.c_int, lib.mosquitto_loop_forever, ctx.mosquitto_p, C.c_int, C.c_int)
    # int mosquitto_loop_start(struct mosquitto *mosq);
    bind(C.c_int, lib.mosquitto_loop_start, ctx.mosquitto_p)
    # int mosquitto_loop_stop(struct mosquitto *mosq, bool force);
    bind(C.c_int, lib.mosquitto_loop_stop, ctx.mosquitto_p, C.c_bool)
    # int mosquitto_loop(struct mosquitto *mosq, int timeout, int max_packets);
    bind(C.c_int, lib.mosquitto_loop, ctx.mosquitto_p, C.c_int, C.c_int)
    # int mosquitto_loop_read(struct mosquitto *mosq, int max_packets);
    bind(C.c_int, lib.mosquitto_loop_read, ctx.mosquitto_p, C.c_int)
    # int mosquitto_loop_write(struct mosquitto *mosq, int max_packets);
    bind(C.c_int, lib.mosquitto_loop_write, ctx.mosquitto_p, C.c_int)
    # int mosquitto_loop_misc(struct mosquitto *mosq);
    bind(C.c_int, lib.mosquitto_loop_misc, ctx.mosquitto_p)
    # int mosquitto_socket(struct mosquitto *mosq);
    bind(C.c_int, lib.mosquitto_socket, ctx.mosquitto_p)
    # bool mosquitto_want_write(struct mosquitto *mosq);
    bind(C.c_bool, lib.mosquitto_want_write, ctx.mosquitto_p)
    # int mosquitto_threaded_set(struct mosquitto *mosq, bool threaded);
    bind(C.c_int, lib.mosquitto_threaded_set, ctx.mosquitto_p, C.c_bool)
    # int mosquitto_opts_set(struct mosquitto *mosq, enum mosq_opt_t option, void *value);
    bind(C.c_int, lib.mosquitto_opts_set, ctx.mosquitto_p, ctx.mosq_opt_t, C.c_void_p)
    # int mosquitto_int_option(struct mosquitto *mosq, enum mosq_opt_t option, int value);
    bind(C.c_int, lib.mosquitto_int_option, ctx.mosquitto_p, ctx.mosq_opt_t, C.c_int)
    # int mosquitto_string_option(struct mosquitto *mosq, enum mosq_opt_t option, const char *value);
    bind(
        C.c_int,
        lib.mosquitto_string_option,
        ctx.mosquitto_p,
        ctx.mosq_opt_t,
        C.c_char_p,
    )
    # int mosquitto_void_option(struct mosquitto *mosq, enum mosq_opt_t option, void *value);
    bind(
        C.c_int, lib.mosquitto_void_option, ctx.mosquitto_p, ctx.mosq_opt_t, C.c_void_p
    )
    # int mosquitto_reconnect_delay_set(struct mosquitto *mosq, unsigned int reconnect_delay, unsigned int reconnect_delay_max, bool reconnect_exponential_backoff);
    bind(
        C.c_int,
        lib.mosquitto_reconnect_delay_set,
        ctx.mosquitto_p,
        C.c_uint,
        C.c_uint,
        C.c_bool,
    )
    # int mosquitto_max_inflight_messages_set(struct mosquitto *mosq, unsigned int max_inflight_messages);
    bind(C.c_int, lib.mosquitto_max_inflight_messages_set, ctx.mosquitto_p, C.c_uint)
    # void mosquitto_message_retry_set(struct mosquitto *mosq, unsigned int message_retry);
    bind(None, lib.mosquitto_message_retry_set, ctx.mosquitto_p, C.c_uint)
    # void mosquitto_user_data_set(struct mosquitto *mosq, void *obj);
    bind(None, lib.mosquitto_user_data_set, ctx.mosquitto_p, C.c_void_p)
    # void *mosquitto_userdata(struct mosquitto *mosq);
    bind(C.c_void_p, lib.mosquitto_userdata, ctx.mosquitto_p)
    # int mosquitto_tls_insecure_set(struct mosquitto *mosq, bool value);
    bind(C.c_int, lib.mosquitto_tls_insecure_set, ctx.mosquitto_p, C.c_bool)
    # int mosquitto_tls_opts_set(struct mosquitto *mosq, int cert_reqs, const char *tls_version, const char *ciphers);
    bind(
        C.c_int,
        lib.mosquitto_tls_opts_set,
        ctx.mosquitto_p,
        C.c_int,
        C.c_char_p,
        C.c_char_p,
    )
    # int mosquitto_tls_psk_set(struct mosquitto *mosq, const char *psk, const char *identity, const char *ciphers);
    bind(
        C.c_int,
        lib.mosquitto_tls_psk_set,
        ctx.mosquitto_p,
        C.c_char_p,
        C.c_char_p,
        C.c_char_p,
    )
    # void *mosquitto_ssl_get(struct mosquitto *mosq);
    bind(C.c_void_p, lib.mosquitto_ssl_get, ctx.mosquitto_p)
    # int mosquitto_socks5_set(struct mosquitto *mosq, const char *host, int port, const char *username, const char *password);
    bind(
        C.c_int,
        lib.mosquitto_socks5_set,
        ctx.mosquitto_p,
        C.c_char_p,
        C.c_int,
        C.c_char_p,
        C.c_char_p,
    )
    # const char *mosquitto_strerror(int mosq_errno);
    bind(C.c_char_p, lib.mosquitto_strerror, C.c_int)
    # const char *mosquitto_connack_string(int connack_code);
    bind(C.c_char_p, lib.mosquitto_connack_string, C.c_int)
    # const char *mosquitto_reason_string(int reason_code);
    bind(C.c_char_p, lib.mosquitto_reason_string, C.c_int)
    # int mosquitto_string_to_command(const char *str, int *cmd);
    bind(C.c_int, lib.mosquitto_string_to_command, C.c_char_p, ctx.int_p)
    # int mosquitto_sub_topic_tokenise(const char *subtopic, char ***topics, int *count);
    bind(C.c_int, lib.mosquitto_sub_topic_tokenise, C.c_char_p, ctx.char_ppp, ctx.int_p)
    # int mosquitto_sub_topic_tokens_free(char ***topics, int count);
    bind(C.c_int, lib.mosquitto_sub_topic_tokens_free, ctx.char_ppp, C.c_int)
    # int mosquitto_topic_matches_sub(const char *sub, const char *topic, bool *result);
    bind(C.c_int, lib.mosquitto_topic_matches_sub, C.c_char_p, C.c_char_p, ctx.bool_p)
    # int mosquitto_topic_matches_sub2(const char *sub, size_t sublen, const char *topic, size_t topiclen, bool *result);
    bind(
        C.c_int,
        lib.mosquitto_topic_matches_sub2,
        C.c_char_p,
        C.c_size_t,
        C.c_char_p,
        C.c_size_t,
        ctx.bool_p,
    )
    # int mosquitto_pub_topic_check(const char *topic);
    bind(C.c_int, lib.mosquitto_pub_topic_check, C.c_char_p)
    # int mosquitto_pub_topic_check2(const char *topic, size_t topiclen);
    bind(C.c_int, lib.mosquitto_pub_topic_check2, C.c_char_p, C.c_size_t)
    # int mosquitto_sub_topic_check(const char *topic);
    bind(C.c_int, lib.mosquitto_sub_topic_check, C.c_char_p)
    # int mosquitto_sub_topic_check2(const char *topic, size_t topiclen);
    bind(C.c_int, lib.mosquitto_sub_topic_check2, C.c_char_p, C.c_size_t)
    # int mosquitto_validate_utf8(const char *str, int len);
    bind(C.c_int, lib.mosquitto_validate_utf8, C.c_char_p, C.c_int)
    # int mosquitto_subscribe_simple( struct mosquitto_message **messages, int msg_count, bool want_retained, const char *topic, int qos, const char *host, int port, const char *client_id, int keepalive, bool clean_session, const char *username, const char *password, const struct libmosquitto_will *will, const struct libmosquitto_tls *tls);
    bind(
        C.c_int,
        lib.mosquitto_subscribe_simple,
        ctx.mosquitto_message_pp,
        C.c_int,
        C.c_bool,
        C.c_char_p,
        C.c_int,
        C.c_char_p,
        C.c_int,
        C.c_char_p,
        C.c_int,
        C.c_bool,
        C.c_char_p,
        C.c_char_p,
        ctx.libmosquitto_will_p,
        ctx.libmosquitto_tls_p,
    )
    # int mosquitto_property_add_byte(mosquitto_property **proplist, int identifier, uint8_t value);
    bind(
        C.c_int,
        lib.mosquitto_property_add_byte,
        ctx.mosquitto_property_pp,
        C.c_int,
        C.c_uint8,
    )
    # int mosquitto_property_add_int16(mosquitto_property **proplist, int identifier, uint16_t value);
    bind(
        C.c_int,
        lib.mosquitto_property_add_int16,
        ctx.mosquitto_property_pp,
        C.c_int,
        C.c_uint16,
    )
    # int mosquitto_property_add_int32(mosquitto_property **proplist, int identifier, uint32_t value);
    bind(
        C.c_int,
        lib.mosquitto_property_add_int32,
        ctx.mosquitto_property_pp,
        C.c_int,
        C.c_uint32,
    )
    # int mosquitto_property_add_varint(mosquitto_property **proplist, int identifier, uint32_t value);
    bind(
        C.c_int,
        lib.mosquitto_property_add_varint,
        ctx.mosquitto_property_pp,
        C.c_int,
        C.c_uint32,
    )
    # int mosquitto_property_add_binary(mosquitto_property **proplist, int identifier, const void *value, uint16_t len);
    bind(
        C.c_int,
        lib.mosquitto_property_add_binary,
        ctx.mosquitto_property_pp,
        C.c_int,
        C.c_void_p,
        C.c_uint16,
    )
    # int mosquitto_property_add_string(mosquitto_property **proplist, int identifier, const char *value);
    bind(
        C.c_int,
        lib.mosquitto_property_add_string,
        ctx.mosquitto_property_pp,
        C.c_int,
        C.c_char_p,
    )
    # int mosquitto_property_add_string_pair(mosquitto_property **proplist, int identifier, const char *name, const char *value);
    bind(
        C.c_int,
        lib.mosquitto_property_add_string_pair,
        ctx.mosquitto_property_pp,
        C.c_int,
        C.c_char_p,
        C.c_char_p,
    )
    # int mosquitto_property_identifier(const mosquitto_property *property);
    bind(C.c_int, lib.mosquitto_property_identifier, ctx.mosquitto_property_p)
    # const mosquitto_property *mosquitto_property_next(const mosquitto_property *proplist);
    bind(
        ctx.mosquitto_property_p, lib.mosquitto_property_next, ctx.mosquitto_property_p
    )
    # const mosquitto_property *mosquitto_property_read_byte( const mosquitto_property *proplist, int identifier, uint8_t *value, bool skip_first);
    bind(
        ctx.mosquitto_property_p,
        lib.mosquitto_property_read_byte,
        ctx.mosquitto_property_p,
        C.c_int,
        ctx.uint8_t_p,
        C.c_bool,
    )
    # const mosquitto_property *mosquitto_property_read_int16( const mosquitto_property *proplist, int identifier, uint16_t *value, bool skip_first);
    bind(
        ctx.mosquitto_property_p,
        lib.mosquitto_property_read_int16,
        ctx.mosquitto_property_p,
        C.c_int,
        ctx.uint16_t_p,
        C.c_bool,
    )
    # const mosquitto_property *mosquitto_property_read_int32( const mosquitto_property *proplist, int identifier, uint32_t *value, bool skip_first);
    bind(
        ctx.mosquitto_property_p,
        lib.mosquitto_property_read_int32,
        ctx.mosquitto_property_p,
        C.c_int,
        ctx.uint32_t_p,
        C.c_bool,
    )
    # const mosquitto_property *mosquitto_property_read_varint( const mosquitto_property *proplist, int identifier, uint32_t *value, bool skip_first);
    bind(
        ctx.mosquitto_property_p,
        lib.mosquitto_property_read_varint,
        ctx.mosquitto_property_p,
        C.c_int,
        ctx.uint32_t_p,
        C.c_bool,
    )
    # const mosquitto_property *mosquitto_property_read_binary( const mosquitto_property *proplist, int identifier, void **value, uint16_t *len, bool skip_first);
    bind(
        ctx.mosquitto_property_p,
        lib.mosquitto_property_read_binary,
        ctx.mosquitto_property_p,
        C.c_int,
        ctx.void_pp,
        ctx.uint16_t_p,
        C.c_bool,
    )
    # const mosquitto_property *mosquitto_property_read_string( const mosquitto_property *proplist, int identifier, char **value, bool skip_first);
    bind(
        ctx.mosquitto_property_p,
        lib.mosquitto_property_read_string,
        ctx.mosquitto_property_p,
        C.c_int,
        ctx.char_pp,
        C.c_bool,
    )
    # const mosquitto_property *mosquitto_property_read_string_pair( const mosquitto_property *proplist, int identifier, char **name, char **value, bool skip_first);
    bind(
        ctx.mosquitto_property_p,
        lib.mosquitto_property_read_string_pair,
        ctx.mosquitto_property_p,
        C.c_int,
        ctx.char_pp,
        ctx.char_pp,
        C.c_bool,
    )
    # void mosquitto_property_free_all(mosquitto_property **properties);
    bind(None, lib.mosquitto_property_free_all, ctx.mosquitto_property_pp)
    # int mosquitto_property_copy_all(mosquitto_property **dest, const mosquitto_property *src);
    bind(
        C.c_int,
        lib.mosquitto_property_copy_all,
        ctx.mosquitto_property_pp,
        ctx.mosquitto_property_p,
    )
    # int mosquitto_property_check_command(int command, int identifier);
    bind(C.c_int, lib.mosquitto_property_check_command, C.c_int, C.c_int)
    # int mosquitto_property_check_all(int command, const mosquitto_property *properties);
    bind(C.c_int, lib.mosquitto_property_check_all, C.c_int, ctx.mosquitto_property_p)
    # const char *mosquitto_property_identifier_to_string(int identifier);
    bind(C.c_char_p, lib.mosquitto_property_identifier_to_string, C.c_int)
    # int mosquitto_string_to_property_info(const char *propname, int *identifier, int *type);
    bind(
        C.c_int, lib.mosquitto_string_to_property_info, C.c_char_p, ctx.int_p, ctx.int_p
    )
