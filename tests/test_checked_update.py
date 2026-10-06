import subprocess
import tempfile
from pathlib import Path
from unittest import TestCase,mock
from tools import checked_update

class UpdateTests(TestCase):
    def git(self,root,*args):
        return subprocess.run(['git',*args],cwd=root,check=True,capture_output=True,text=True).stdout.strip()
    def test_candidate_pass_failure_and_dirty_protection(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);origin=root/'origin';origin.mkdir()
            self.git(origin,'init','-b','main');self.git(origin,'config','user.email','test@example.invalid');self.git(origin,'config','user.name','Test')
            (origin/'bootstrap.sh').write_text('exit 0\n');self.git(origin,'add','.');self.git(origin,'commit','-m','initial')
            local=root/'local';self.git(root,'clone',str(origin),str(local));self.git(local,'config','user.email','test@example.invalid');self.git(local,'config','user.name','Test')
            (origin/'new.txt').write_text('candidate');self.git(origin,'add','.');self.git(origin,'commit','-m','candidate')
            with mock.patch.object(checked_update,'ROOT',local):
                old=self.git(local,'rev-parse','HEAD')
                self.assertEqual(checked_update.update(True)['status'],'tested');self.assertEqual(self.git(local,'rev-parse','HEAD'),old)
                self.assertEqual(checked_update.update()['status'],'updated')
                self.assertEqual(checked_update.update()['status'],'current')
                (local/'dirty').write_text('preserve')
                with self.assertRaises(ValueError):checked_update.update()
                (local/'dirty').unlink()
                (origin/'bootstrap.sh').write_text('exit 1\n');self.git(origin,'add','.');self.git(origin,'commit','-m','bad candidate')
                before=self.git(local,'rev-parse','HEAD')
                with self.assertRaises(subprocess.CalledProcessError):checked_update.update()
                self.assertEqual(self.git(local,'rev-parse','HEAD'),before)
