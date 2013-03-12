from misc import get_cmd

blocks = 200 * 20 * 6
hard_drive = [(0, blocks, True)]
file_table = {}

class HardDrive(object):
    class ATItem(object):
        def __init__(self, start, n):
            self.start = start
            self.n = n


        def merge(self, another):
            return HardDrive.ATItem(min(self.start, another.start),
                                    self.start + another.start)


        def __iter__(self):
            return iter([self.start, self.n])


        def __nonzero__(self):
            return self.n


        def __str__(self):
            return '% 10s | % 10s' % (self.start, self.n)


    def __init__(self):
        self._allocation_table = [HardDrive.ATItem(0, 6 * 200 * 20)]
        self._file_table = {}


    def allocate(self, filename, blocks_required):
        if filename in self._file_table:
            return False, -1
        for i, (start, n) in enumerate(self._allocation_table):
            if n > blocks_required:
                self._file_table[filename] = HardDrive.ATItem(start, blocks_required)

                self._allocation_table[i].start += blocks_required
                self._allocation_table[i].n -= blocks_required

                break
        else:
            return False, 0

        self._allocation_table = filter(bool, self._allocation_table)
        s = self._file_table[filename].start
        return True, {'sector': s % 6,
                      'track': (s / 6) % 20,
                      'cylinder': (s / 6) / 20}


    def _insert(self, item):
        idx = 0
        for i, _item in reversed(tuple(enumerate(self._allocation_table))):
            if _item.start < item.start:
                idx = i + 1
                break
        self._allocation_table.insert(idx, item)


    def recycle(self, filename):
        if filename not in self._file_table:
            return False

        start, n = self._file_table[filename]
        del self._file_table[filename]

        self._insert(HardDrive.ATItem(start, n))

        stack = [self._allocation_table[0]]
        for item in self._allocation_table[1:]:
            if stack[-1].start + stack[-1].n == item.start:
                stack[-1].n += item.n
            else:
                stack.append(item)
        self._allocation_table = stack

        return True




def dispatch_command(hard_drive):
    cmd = raw_input('> ')
    if cmd[0] == 'h':
        print 'h(elp)                -- print this text'
        print 'a(llocate)            -- request for file allocation', 'type `a\' or `a filename blocks\''
        print 'r(ecycle)             -- recycle file', 'type `r\' or `r filename'
        print 'd(isplay)             -- display the content of the free space table'
        print 'display (f)ile table  -- display the content of the file table'
    elif cmd[0] == 'a':
        args = get_cmd(cmd, '%c %s %i', hint='filename blocks')
        if not args:
            return

        ret, _ = hard_drive.allocate(*args)
        if ret:
            print 'allocated (track: %(track)s, cylinder: %(cylinder)s, sector: %(sector)s)' % _
        else:
            if _ == 0:
                print 'allocation failed: not enough space'
            elif _ == -1:
                print 'allocation failed: file already exists'
    elif cmd[0] == 'r':
        args = get_cmd(cmd, '%c %s', hint='filename')
        if not args:
            return

        (filename,) = args
        ret = hard_drive.recycle(filename)
        if ret:
            print 'file recycle succeeded'
        else:
            print 'file not found'
    elif cmd[0] == 'd':
        print '% 10s | % 10s' % ('start', 'blocks')
        for item in hard_drive._allocation_table:
            print item
    elif cmd[0] == 'f':
        print '% 10s | % 10s | % 10s' % ('filename', 'start', 'blocks')
        for filename, item in sorted(hard_drive._file_table.iteritems(), key=lambda (k, _): k):
            print '% 10s | %s' % (filename, item)



if __name__ == '__main__':
    hd = HardDrive()
    while True:
        dispatch_command(hd)



