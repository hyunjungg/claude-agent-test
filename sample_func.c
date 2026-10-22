static char *
make_copy (const char *s, size_t n)
{
  char *buf = xmalloc (n + 1);
  memcpy (buf, s, n);
  buf[n] = '\0';
  return buf;
}
