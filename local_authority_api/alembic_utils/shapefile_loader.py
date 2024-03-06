from subprocess import Popen, PIPE


def load_shapefile(op, shapefile, table):
    # shp2pgsql likes to set these when it starts, so make sure we store before and reset after
    conn = op.get_bind()
    res = conn.exec_driver_sql("SHOW client_encoding;")
    client_encoding = res.fetchall()[0][0]
    res = conn.exec_driver_sql("SHOW standard_conforming_strings;")
    standard_conforming_strings = res.fetchall()[0][0]

    # Run command
    cmd = "shp2pgsql -e -a -s 27700 {} {}".format(shapefile, table)
    process = Popen(cmd.split(), stdout=PIPE)
    while True:
        output = process.stdout.readline().decode('UTF8')
        if process.poll() is not None and output == '':
            break
        op.execute(output)

    if process.poll() != 0:
        raise Exception("shp2pgsql command failed with exit code {}".format(process.poll()))

    op.execute("SET client_encoding TO {}".format(client_encoding))
    op.execute("SET standard_conforming_strings TO {}".format(standard_conforming_strings))
