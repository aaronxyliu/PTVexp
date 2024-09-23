import re

class StandardVersion:
    def __init__(self, version_str: str):
        version_str = str(version_str)
        self.major_version = self.minor_version = self.patch_version = self.suffix = None
        res1 = re.search('[0-9]+', version_str)
        if res1:
            self.major_version = res1.group()   
            version_str = version_str[res1.span()[1]:]

            res2 = re.search('[0-9]+', version_str)
            if res2:
                self.minor_version = res2.group()   
                version_str = version_str[res2.span()[1]:]

                res3 = re.search('[0-9]+', version_str)
                if res3:
                    self.patch_version = res3.group()   
                    version_str = version_str[res3.span()[1]:]
        self.suffix = version_str
        
    def __eq__(self, x: object) -> bool:
        if not self.major_version or not x.major_version:
            return False
        if self.major_version != x.major_version:
            return False
        if not self.minor_version or not x.minor_version:
            return True
        if self.minor_version != x.minor_version:
            return False
        if not self.patch_version or not x.patch_version:
            return True
        if self.patch_version != x.patch_version:
            return False
        return True
        # if not self.suffix or not x.suffix:
        #     return True
        # if self.suffix != x.suffix:
        #     return False
        
    def __str__(self) -> str:
        print_content = f'''Major version: {self.major_version}\n\
Minor version: {self.minor_version}\n\
Patch version: {self.patch_version}\n\
Suffix: {self.suffix}
        '''
        return print_content
