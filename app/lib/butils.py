# -*- coding: utf-8 -*-
import os, sys, re, time, hashlib, StringIO, traceback
from time import sleep, time as now

# Update 2015/12/21

class Butils():

    base_delay = 134
    STANDAR_TIME_FORMAT = "%d/%m/%Y %H:%M:%S"
    COMPRESSED_TIME_FORMAT = "%Y%m%d%H%M%S"
    HASH_TYPES = {
            "md5" : hashlib.md5,
            "sha1": hashlib.sha1,
            "sha256": hashlib.sha256,
            "sha512": hashlib.sha512
        }
    BLOCK_SIZE = 512

    @staticmethod
    def filterUnicode(*args):
        _range = range(0x20, 0x7f)
        nargs = list(args)
        for i, arg in enumerate(nargs):
            if type(arg) == unicode:
                try:
                    nargs[i] = arg.encode("iso-8859-1")
                except UnicodeEncodeError as e:
                    nargs[i] = arg.encode("utf-8")
            else:
                nargs[i] = str(arg)
        return "".join([
            "".join([
                chr(ord(c)) if ord(c) in _range else "\\x%s" % hex(ord(c)).replace("0x", "").zfill(2)
                for c in e
                ])
            for e in nargs])

    @staticmethod
    def getHexString(*args):
        return "".join([
            "".join([
                "%s" % hex(ord(c)).replace("0x", "").zfill(2)
                for c in e 
                ])
            for e in args])

    @staticmethod
    def countLines(files):
        lines = {
            fi : len([
                l
                for l in open(fi, "r") if (l.strip() and \
                    (not(re.match(r"(\#)", l.strip()))) )
                ])
            for fi in files
        }

        return {"total" : sum(lines.values()), "files":lines}

    @staticmethod
    def getStrftime(_time=now(), _format=STANDAR_TIME_FORMAT):
        return time.strftime( _format, time.localtime( _time ) )

    @staticmethod
    def getComplexHash(obj, hashtype):
        hs = Butils.HASH_TYPES[hashtype]()
        if type(obj) in [str, unicode]:
            if type(obj) == unicode:
                obj = obj.encode("iso-8859-1")
            _len = len(obj)
            io = StringIO.StringIO(obj)
            dt = None
            while dt != "":
                dt = io.read(Butils.BLOCK_SIZE)
                hs.update(dt)
            io.close()

        elif type(obj) == dict:
            for key in sorted(obj.keys()):
                value = obj[key]
                hs.update(Butils.getComplexHash(key, hashtype))
                hs.update(Butils.getComplexHash(value, hashtype))
        else:
            hs.update(str(obj))
        return hs.hexdigest()

    @staticmethod
    def walk(basedir, allow_pattern = None, deny_pattern = None, verbose=True):
        _error = False
        root = basedir.replace("\\", "/")
        try:
            names = os.listdir(basedir)
        except (IOError, OSError) as e:
            if verbose:
                traceback.print_exc()
            _error = True
        if not _error:
            dnames = [
                name
                for name in names
                if os.path.isdir(os.path.join(root, name)) and \
                    not os.path.islink(os.path.join(root, name))
                ]
            fnames = [
                name
                for name in names
                if os.path.isfile(os.path.join(root, name)) and \
                    not os.path.islink(os.path.join(root, name))
                ]
            yield root, sorted(dnames), sorted(fnames)
            dnames = sorted(dnames)
            if allow_pattern is not None:
                true_dirs = []
                false_dirs = []
                for dn in dnames:
                    if re.search( allow_pattern, os.path.join(root, dn+"/").replace("\\", "/") ):
                        true_dirs.append(dn)
                    else:
                        false_dirs.append(dn)
                true_dirs.extend(false_dirs)
                dnames = true_dirs
            for dname in dnames:
                nroot = os.path.join(root, dname).replace("\\", "/")
                if (deny_pattern is not None and re.search(deny_pattern, nroot) ):
                    if verbose:
                        print "omit", nroot
                    continue
                # if (allow_pattern is not None and not re.search(allow_pattern, nroot) ):
                #     print "omit", nroot
                #     continue
                for nroot, ndnames, nfnames in Butils.walk(nroot,
                        allow_pattern = allow_pattern,
                        deny_pattern = deny_pattern,
                        verbose = verbose ):
                    yield nroot, ndnames, nfnames

    @staticmethod
    def callOnWalk(basedir, callback, allow_pattern, deny_pattern, *args, **kargs):
        # for root, dnames, fnames in os.walk(basedir):
        for root, dnames, fnames in Butils.walk(basedir, allow_pattern, deny_pattern):
            root = root.replace("\\", "/")
            if (deny_pattern is not None and re.search(deny_pattern, root) ): continue
            for fn in fnames:
                ffname = os.path.join(root, fn).replace("\\", "/")
                if (deny_pattern is not None and     re.search(deny_pattern, ffname) ): continue
                if (allow_pattern is not None and not re.search(allow_pattern, ffname) ): continue
                # print args, kargs
                callback(basedir, root, fn, *args, **kargs)
            yield root, dnames, fnames

    @staticmethod
    def makedirs(path):
        try:
            if not os.path.lexists(path):
                os.makedirs(path)
            return True, path
        except IOError as e:
            return False, e

    @staticmethod
    def lexistsOrCreate(path):
        dname = os.path.dirname(path)
        if Butils.makedirs(dname)[0]:
            if os.path.lexists(path):
                return True
            else:
                with open(path, "wb"): pass
                return False
        else:
            return False

    @staticmethod
    def getHumanNum(num):
        limits = {
                0x400      : "KiB",
                0x100000   : "MiB",
                0x40000000 : "GiB"
            }
        for limit in sorted(limits)[::-1]:
            unit = limits[limit]
            if num >= limit:
                return num / float(limit), unit
        return float(num), "B"

    @staticmethod
    def getPattern(_list):
        return "(" + ")|(".join([e for e in _list]) + ")"

    @staticmethod
    def formatForJSON(obj):

        if type(obj) == dict:
            for key, value in obj.copy().iteritems():
                if not type(key) in [str, unicode]:
                    obj.pop(key)
                    key = str(key)
                obj[ key ] = Butils.formatForJSON(value)
            return obj
        elif type(obj) == set:
            return list(obj)
        else:
            return obj

class Log():

    log_path = None
    log_file = None
    log_format = 0
    name = None
    TXT = 0
    CSV = 1

    def __init__(self, master, path = None, log_format = 0, headers = None, overwrite = False):
        self.master = master
        self.log_format = log_format
        self.overwrite = overwrite
        if path is not None:
            self.setLogFile(path)
        if log_format == self.CSV:
            if path is None:
                print "ERROR: No filename specified for type CSV"
            elif headers is None:
                print "ERROR: No headers specified for type CSV"
            else:
                try:
                    if os.path.getsize(self.log_path) == 0:
                        self.writeLine(headers)
                except Exception as e:
                    print "ERROR:", e


    def setLogFile(self, path):
        self.log_path = path
        self.name = path
        self.log_file = open(self.log_path,"wb" if self.overwrite else "wb" if self.log_format == self.TXT \
            else ("ab" if self.log_format == self.CSV else "rb"))
        self.master.addOpenFile(self.log_file)

    def write(self, st):
        if(not self.log_file.closed):
            self.log_file.write(st)
        else:
            print "ERROR: Log file", self.log_path, "is closed"

    def writeLine(self, st):
        if self.log_format == self.TXT:
            if(not self.log_file.closed):
                self.log_file.write(st+"\n")
            else:
                print "ERROR: Log file", self.log_path, "is closed"
        elif self.log_format == self.CSV:
            if type(st) == list or type(st) == tuple:
                self.log_file.write(";".join(list(st))+"\n")
            else:
                print "ERROR: Invalid argument", st

    def flush(self):
        if(not self.log_file.closed):
            self.log_file.flush()
        else:
            print "ERROR: Log file", self.log_path, "is closed"

    def close(self):
        self.closed = True
        if not self.closed: self.log_file.close()

    # def closed(self):
    #     return self.log_file.closed

if __name__ == "__main__":
    print Butils.filterUnicode("aksdk´ñk+çìpºº0921f\x01\x02\x03", "09813741çç´ñ+`.º098")
    print Butils.getHexString("aksdk´ñk+çìpºº0921f\x01\x02\x03", "09813741çç´ñ+`.º098")
    print re.search(r"(Clase\/02DWCC\/2Ao)", "H:\Clase\02DWCC\2Ao" \
            .replace("\x5c", "/"))
    print r"H:\Clase\02DWCC\2Ao".replace("\\", "/")
    print Butils.countLines(["butils.py", "baselib.py"])
    print Butils.getStrftime()
    print len(Butils.getStrftime(_format = Butils.COMPRESSED_TIME_FORMAT))
    st = u"c\xf3ñ"
    # print Butils.getComplexHash({1:"a",2:"b",3:u"c\xf3ñ"}, "md5")
    print Butils.getComplexHash({3:st}, "md5")
    # print hashlib.md5(st).hexdigest()
    print Butils.getHumanNum(1654652000)
    print Butils.getPattern([
            "/\\.dvault",
            "\\.zip\\Z"
        ])