from arambadge import badge
import time
import tasko

MATRIX_ADDR = 52

def back_and_forth(n):
    return list(range(n))+list(range(n - 2, 0, -1))

async def scan_rows():
    for y in back_and_forth(9) + [0]:
        buf = bytearray([0] * 18)
        buf[y*2] = 0xff
        buf[y*2+1] = 0xff
        badge.i2c.writeto(MATRIX_ADDR, buf)
        await tasko.sleep(0.05)

async def scan_cols():
    for x in back_and_forth(10) + [0]:
        buf = bytearray([0] * 18)
        for y in range(9):
            buf[y*2 + x // 8] = 1 << (x % 8)
        badge.i2c.writeto(MATRIX_ADDR, buf)
        await tasko.sleep(0.05)

async def triangles():
    while not badge.left and not badge.right:
        buf = bytearray([0] * 18)
        for y in range(9):
            for x in range(10):
                if x <= y:
                    buf[y*2 + x // 8] |= 1 << (x % 8)
        badge.i2c.writeto(MATRIX_ADDR, buf)
        await tasko.sleep(0.3)

        buf = bytearray([0] * 18)
        for y in range(9):
            for x in range(10):
                if x >= y:
                    buf[y*2 + x // 8] |= 1 << (x % 8)
        badge.i2c.writeto(MATRIX_ADDR, buf)
        await tasko.sleep(0.3)


async def main(addon):
    await tasko.sleep(0.5)

    badge.i2c.try_lock()
    buf = bytearray([0] * 18)
    badge.i2c.writeto(MATRIX_ADDR, buf)

    while True:
        if badge.left:
            await scan_cols()
        if badge.up:
            await triangles()
        if badge.right:
            await scan_rows()
