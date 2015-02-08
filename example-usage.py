import websocket_recorder


if __name__ == '__main__':
        script_filename = sys.argv[0]
        settings_file = sys.argv[1]

        # Load the settings specific to a particular websocket source.
        # The settings ar stored as Python variables. See settings.conf
        # for example config
        execfile(settings_file)

        sys.stdout = open(stdout_file, "a")
        sys.stderr = open(stderr_file, "a")
        recorder = WebsocketRecorder(url, msg_to_send, max_lines, script_filename, machine_id, ws_name, extra_meta_data)
        recorder.connect()
        recorder.run_forever()
