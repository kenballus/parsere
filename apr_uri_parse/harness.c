#include <stdlib.h>
#include <string.h>

#include <apr_uri.h>

#define MAX_URL_LEN (32768)
static char url_string[MAX_URL_LEN + 1];

int main(void) {
    fread(url_string, 1, MAX_URL_LEN, stdin);

    apr_initialize();

    apr_pool_t *pool;
    apr_pool_create(&pool, NULL);

    apr_uri_t result;
    int const rc = apr_uri_parse(pool, url_string, &result);

    apr_terminate();
    return rc;
}
