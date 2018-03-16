from os import urandom
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

class AESCipher:
    """ Wrapper for cryptography aes cipher.

    :attr char: padding_value(char): padding character used for encryption.
    """
    padding_value = '\0'

    def __init__(self, key, iv_length):
        """
        Cipher constructor.

        :param str key: AES key
        :param str iv: initialization vector
        """
        self._key = key
        self._iv_length = iv_length
        self._cipher = Cipher(algorithms.AES(key), modes.CBC(urandom(iv_length)), backend=default_backend())

    def encrypt(self, content):
        """
        Encrypt string using (key, iv) pair.
        Uses padding_value if content has wrong padding.

        :param str content: unencrypted string.

        :returns: Encrypted string.
        """
        padding = len(content) % 16
        if padding != 0:
            content += ''.join(self.padding_value for i in range(16 - padding))

        iv = urandom(self._iv_length)
        self._cipher.mode = modes.CBC(iv)
        encryptor = self._cipher.encryptor()
        ct = encryptor.update(content) + encryptor.finalize()
        return iv + ct

    def decrypt(self, content):
        """
        Decrypt string using (key, iv) pair.
        Removes padding_value from the end.

        :param str content: encrypted string.

        :returns: Unencrypted string.
        """
        iv = content[:self._iv_length]
        self._cipher.mode = modes.CBC(iv)
        decryptor = self._cipher.decryptor()
        content = decryptor.update(content[self._iv_length:]) + decryptor.finalize()
        return content.rstrip(self.padding_value)

    def encrypt_file(self, in_filename):
        """
        Encrypt file content using (key, iv) pair.
        Uses padding_value if content has wrong padding.

        :param str in_filename(in_filename): unencrypted data file name.

        :returns: Encrypted string.
        """
        with open(in_filename, "rb") as file:
            content = file.read()
        return self.encrypt(content)

    def decrypt_file(self, in_filename):
        """
        Decrypt file using (key, iv) pair.
        Removes padding_value from the end.

        :param str out_filename(out_filename): encrypted data file name.

        :returns: Unencrypted string.
        """
        with open(in_filename, "rb") as file:
            content = file.read()
        return self.decrypt(content)

    def encrypt_file_save_file(self, in_filename, out_filename):
        """
        Encrypt file using (key, iv) pair and save result in a file.
        Uses padding_value if content has wrong padding.

        :param str in_filename(in_filename): unencrypted data file name.
        :param str out_filename(out_filename): encrypted data file name.
        """
        content = self.encrypt_file(in_filename)
        with open(out_filename, "wb+") as out:
            out.write(content)

    def decrypt_file_save_file(self, in_filename, out_filename):
        """
        Decrypt file using (key, iv) pair and save result in a file.
        Removes padding_value from the end.

        :param str in_filename(in_filename): encrypted data file name.
        :param str out_filename(out_filename): unencrypted data file name.
        """
        content = self.decrypt_file(in_filename)
        with open(out_filename, "wb+") as out:
            out.write(content)
        